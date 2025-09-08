#!/usr/bin/env python3
"""
Salesforce New Grad Job Scraper
Monitors Salesforce careers page for new grad software engineering positions
"""

import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import hashlib
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dataclasses import dataclass, asdict
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('salesforce_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobPosting:
    title: str
    location: str
    team: str
    job_id: str
    url: str
    posted_date: str
    hash_id: str

class SalesforceJobScraper:
    def __init__(self, db_path: str = "salesforce_jobs.db"):
        self.base_url = "https://careers.salesforce.com/en/jobs/"
        self.search_params = {
            "search": "",
            "team": "Software+Engineering",
            "jobtype": "New+Grads",
            "pagesize": "20"
        }
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database to store job postings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                location TEXT NOT NULL,
                team TEXT NOT NULL,
                job_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                posted_date TEXT NOT NULL,
                hash_id TEXT UNIQUE NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                jobs_found INTEGER,
                new_jobs INTEGER,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def get_job_hash(self, job_data: Dict) -> str:
        """Generate a unique hash for a job posting"""
        content = f"{job_data['title']}{job_data['location']}{job_data['team']}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def scrape_jobs(self) -> List[JobPosting]:
        """Scrape job postings from Salesforce careers page"""
        try:
            url = f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in self.search_params.items()])}#results"
            logger.info(f"Scraping URL: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Find job listings - they appear to be in a structured format
            job_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in x.lower() if x else False)
            
            if not job_elements:
                # Try alternative selectors based on the page structure
                job_elements = soup.find_all('div', string=lambda text: text and 'Software Engineering' in text)
                if not job_elements:
                    # Look for any elements containing job titles
                    job_elements = soup.find_all(['h3', 'h4', 'div'], string=lambda text: text and any(
                        keyword in text.lower() for keyword in ['engineer', 'developer', 'software', 'new grad', 'graduate']
                    ))
            
            logger.info(f"Found {len(job_elements)} potential job elements")
            
            # Extract job information
            for element in job_elements:
                try:
                    job_data = self.extract_job_data(element)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Error extracting job data: {e}")
                    continue
            
            # If no jobs found with standard selectors, try to parse the page differently
            if not jobs:
                jobs = self.fallback_scrape(soup)
            
            logger.info(f"Successfully scraped {len(jobs)} jobs")
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []
    
    def extract_job_data(self, element) -> Optional[JobPosting]:
        """Extract job data from a single job element"""
        try:
            # Try to find title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or element
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            
            # Skip if this doesn't look like a job posting
            if not any(keyword in title.lower() for keyword in ['engineer', 'developer', 'software', 'new grad', 'graduate']):
                return None
            
            # Try to find location
            location = "Unknown Location"
            location_elem = element.find(string=lambda text: text and any(
                loc in text for loc in ['California', 'New York', 'Seattle', 'Austin', 'Remote', 'San Francisco']
            ))
            if location_elem:
                location = location_elem.strip()
            
            # Try to find job URL
            url = ""
            link_elem = element.find('a', href=True)
            if link_elem:
                url = link_elem['href']
                if not url.startswith('http'):
                    url = f"https://careers.salesforce.com{url}"
            
            # Generate job ID from title and location
            job_id = hashlib.md5(f"{title}{location}".encode()).hexdigest()[:12]
            
            job_data = {
                'title': title,
                'location': location,
                'team': 'Software Engineering',
                'job_id': job_id,
                'url': url,
                'posted_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            job_data['hash_id'] = self.get_job_hash(job_data)
            
            return JobPosting(**job_data)
            
        except Exception as e:
            logger.warning(f"Error extracting job data from element: {e}")
            return None
    
    def fallback_scrape(self, soup) -> List[JobPosting]:
        """Fallback scraping method when standard selectors fail"""
        jobs = []
        try:
            # Look for any text that might be job titles
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['software engineer', 'new grad', 'graduate', 'entry level']):
                    if len(line) < 100:  # Reasonable title length
                        job_data = {
                            'title': line,
                            'location': 'Unknown Location',
                            'team': 'Software Engineering',
                            'job_id': hashlib.md5(line.encode()).hexdigest()[:12],
                            'url': '',
                            'posted_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        job_data['hash_id'] = self.get_job_hash(job_data)
                        jobs.append(JobPosting(**job_data))
            
            logger.info(f"Fallback scraping found {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Fallback scraping failed: {e}")
        
        return jobs
    
    def save_jobs(self, jobs: List[JobPosting]) -> int:
        """Save jobs to database and return count of new jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_jobs = 0
        
        for job in jobs:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO job_postings 
                    (title, location, team, job_id, url, posted_date, hash_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (job.title, job.location, job.team, job.job_id, job.url, job.posted_date, job.hash_id))
                
                if cursor.rowcount > 0:
                    new_jobs += 1
                    logger.info(f"New job found: {job.title} - {job.location}")
                
            except sqlite3.IntegrityError:
                # Job already exists, update last_updated
                cursor.execute('''
                    UPDATE job_postings 
                    SET last_updated = CURRENT_TIMESTAMP 
                    WHERE hash_id = ?
                ''', (job.hash_id,))
        
        # Log this scrape session
        cursor.execute('''
            INSERT INTO scrape_log (jobs_found, new_jobs, status)
            VALUES (?, ?, ?)
        ''', (len(jobs), new_jobs, 'success'))
        
        conn.commit()
        conn.close()
        
        return new_jobs
    
    def get_new_jobs(self, hours: int = 24) -> List[Dict]:
        """Get jobs posted in the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT title, location, team, url, posted_date, first_seen
            FROM job_postings 
            WHERE first_seen >= ?
            ORDER BY first_seen DESC
        ''', (cutoff_time,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'title': row[0],
                'location': row[1],
                'team': row[2],
                'url': row[3],
                'posted_date': row[4],
                'first_seen': row[5]
            })
        
        conn.close()
        return jobs
    
    def send_notification(self, new_jobs: List[Dict], email_config: Dict = None):
        """Send notification about new jobs"""
        if not new_jobs:
            return
        
        if email_config:
            self.send_email_notification(new_jobs, email_config)
        else:
            # Console notification
            print(f"\n🎉 {len(new_jobs)} NEW JOB(S) FOUND!")
            print("=" * 50)
            for job in new_jobs:
                print(f"📋 {job['title']}")
                print(f"📍 {job['location']}")
                print(f"🔗 {job['url'] if job['url'] else 'No URL available'}")
                print(f"📅 Posted: {job['posted_date']}")
                print("-" * 30)
    
    def send_email_notification(self, new_jobs: List[Dict], email_config: Dict):
        """Send email notification about new jobs"""
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            msg['Subject'] = f"🚀 {len(new_jobs)} New Salesforce New Grad Jobs Found!"
            
            body = f"""
            <h2>New Salesforce New Grad Job Postings</h2>
            <p>Found {len(new_jobs)} new job posting(s):</p>
            <ul>
            """
            
            for job in new_jobs:
                body += f"""
                <li>
                    <strong>{job['title']}</strong><br>
                    📍 {job['location']}<br>
                    📅 Posted: {job['posted_date']}<br>
                    🔗 <a href="{job['url']}">{job['url'] if job['url'] else 'No URL available'}</a>
                </li><br>
                """
            
            body += "</ul>"
            body += "<p>Happy job hunting! 🎯</p>"
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['from_email'], email_config['password'])
            text = msg.as_string()
            server.sendmail(email_config['from_email'], email_config['to_email'], text)
            server.quit()
            
            logger.info(f"Email notification sent for {len(new_jobs)} new jobs")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def run_scrape(self, email_config: Dict = None):
        """Run a single scrape session"""
        logger.info("Starting Salesforce job scrape...")
        
        jobs = self.scrape_jobs()
        if not jobs:
            logger.warning("No jobs found - this might indicate a scraping issue")
            return
        
        new_jobs_count = self.save_jobs(jobs)
        
        if new_jobs_count > 0:
            new_jobs = self.get_new_jobs(hours=1)  # Get jobs from last hour
            self.send_notification(new_jobs, email_config)
        else:
            logger.info("No new jobs found")
        
        logger.info(f"Scrape completed. Found {len(jobs)} total jobs, {new_jobs_count} new jobs")

def main():
    """Main function to run the scraper"""
    scraper = SalesforceJobScraper()
    
    # Load email configuration if available
    email_config = None
    if os.path.exists('email_config.json'):
        try:
            with open('email_config.json', 'r') as f:
                email_config = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load email config: {e}")
    
    # Run the scraper
    scraper.run_scrape(email_config)

if __name__ == "__main__":
    main()

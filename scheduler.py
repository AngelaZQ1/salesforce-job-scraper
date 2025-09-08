#!/usr/bin/env python3
"""
Daily Scheduler for Salesforce Job Scraper
Runs the scraper daily at specified times
"""

import schedule
import time
import logging
import json
import os
from datetime import datetime
from salesforce_job_scraper import SalesforceJobScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobScheduler:
    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = config_file
        self.scraper = SalesforceJobScraper()
        self.email_config = self.load_email_config()
        self.schedule_config = self.load_schedule_config()
        
    def load_email_config(self) -> dict:
        """Load email configuration"""
        if os.path.exists('email_config.json'):
            try:
                with open('email_config.json', 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load email config: {e}")
        return None
    
    def load_schedule_config(self) -> dict:
        """Load schedule configuration"""
        default_config = {
            "times": ["09:00", "15:00", "21:00"],  # 9 AM, 3 PM, 9 PM
            "timezone": "local",
            "enabled": True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Could not load schedule config: {e}")
        
        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def run_scrape_job(self):
        """Job function to run the scraper"""
        logger.info("Starting scheduled scrape job...")
        try:
            self.scraper.run_scrape(self.email_config)
            logger.info("Scheduled scrape job completed successfully")
        except Exception as e:
            logger.error(f"Scheduled scrape job failed: {e}")
    
    def setup_schedule(self):
        """Setup the daily schedule"""
        if not self.schedule_config.get("enabled", True):
            logger.info("Scheduler is disabled in config")
            return
        
        times = self.schedule_config.get("times", ["09:00"])
        
        for time_str in times:
            schedule.every().day.at(time_str).do(self.run_scrape_job)
            logger.info(f"Scheduled daily scrape at {time_str}")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        logger.info("Starting job scheduler...")
        self.setup_schedule()
        
        if not schedule.jobs:
            logger.warning("No jobs scheduled!")
            return
        
        logger.info(f"Scheduler running with {len(schedule.jobs)} job(s)")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

def main():
    """Main function to run the scheduler"""
    scheduler = JobScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()

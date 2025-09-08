#!/usr/bin/env python3
"""
Test script for the Salesforce job scraper
"""

from salesforce_job_scraper import SalesforceJobScraper
import json

def test_scraper():
    """Test the scraper functionality"""
    print("🧪 Testing Salesforce Job Scraper...")
    print("=" * 50)
    
    # Initialize scraper
    scraper = SalesforceJobScraper("test_salesforce_jobs.db")
    
    # Test scraping
    print("📡 Scraping jobs...")
    jobs = scraper.scrape_jobs()
    
    if jobs:
        print(f"✅ Found {len(jobs)} jobs:")
        for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
            print(f"  {i}. {job.title}")
            print(f"     📍 {job.location}")
            print(f"     🔗 {job.url if job.url else 'No URL'}")
            print()
        
        if len(jobs) > 5:
            print(f"  ... and {len(jobs) - 5} more jobs")
        
        # Test saving to database
        print("💾 Saving jobs to database...")
        new_jobs = scraper.save_jobs(jobs)
        print(f"✅ Saved {len(jobs)} jobs, {new_jobs} were new")
        
        # Test getting recent jobs
        print("📋 Getting recent jobs...")
        recent_jobs = scraper.get_new_jobs(hours=24)
        print(f"✅ Found {len(recent_jobs)} jobs from last 24 hours")
        
    else:
        print("❌ No jobs found - this might indicate a scraping issue")
        print("   The website structure may have changed or there might be no current postings")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_scraper()

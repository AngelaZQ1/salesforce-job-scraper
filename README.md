# Salesforce New Grad Job Scraper

A Python-based web scraper that monitors Salesforce's careers page for new graduate software engineering positions and sends notifications when new jobs are posted.

## Features

- 🔍 **Automated Scraping**: Monitors Salesforce careers page for new grad software engineering jobs
- 📊 **Data Storage**: Uses SQLite database to track job postings and prevent duplicates
- ⏰ **Daily Scheduling**: Runs automatically at configurable times (default: 9 AM, 3 PM, 9 PM)
- 📧 **Email Notifications**: Sends email alerts when new jobs are found
- 📝 **Comprehensive Logging**: Detailed logs for monitoring and debugging
- 🛡️ **Error Handling**: Robust error handling and fallback mechanisms

## Installation

1. **Clone or download the project files**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Email Notifications (Optional)

1. Copy the example email config:
   ```bash
   cp email_config.json.example email_config.json
   ```

2. Edit `email_config.json` with your email settings:
   ```json
   {
     "from_email": "your-email@gmail.com",
     "to_email": "your-email@gmail.com",
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "password": "your-app-password"
   }
   ```

   **For Gmail users**: You'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### Schedule Configuration

Edit `scheduler_config.json` to customize when the scraper runs:

```json
{
  "times": ["09:00", "15:00", "21:00"],
  "timezone": "local",
  "enabled": true
}
```

- `times`: List of times to run the scraper (24-hour format)
- `enabled`: Set to `false` to disable the scheduler

## Usage

### Run Once (Manual Scrape)

```bash
python salesforce_job_scraper.py
```

### Run Daily Scheduler

```bash
python scheduler.py
```

The scheduler will run continuously and execute scrapes at the configured times.

### Stop the Scheduler

Press `Ctrl+C` to stop the scheduler.

## Output

### Console Output
When new jobs are found, you'll see output like:
```
🎉 2 NEW JOB(S) FOUND!
==================================================
📋 Software Engineer - New Grad
📍 San Francisco, CA
🔗 https://careers.salesforce.com/jobs/...
📅 Posted: 2024-01-15
------------------------------
```

### Database
Job data is stored in `salesforce_jobs.db` SQLite database with the following tables:
- `job_postings`: All job postings with metadata
- `scrape_log`: Log of each scraping session

### Logs
- `salesforce_scraper.log`: Detailed scraper logs
- `scheduler.log`: Scheduler-specific logs

## Files

- `salesforce_job_scraper.py`: Main scraper implementation
- `scheduler.py`: Daily scheduler
- `requirements.txt`: Python dependencies
- `email_config.json.example`: Email configuration template
- `scheduler_config.json`: Schedule configuration
- `salesforce_jobs.db`: SQLite database (created automatically)
- `*.log`: Log files (created automatically)

## Troubleshooting

### No Jobs Found
- The scraper might need to be updated if Salesforce changes their website structure
- Check the logs for any error messages
- Try running the scraper manually to see console output

### Email Notifications Not Working
- Verify your email configuration in `email_config.json`
- For Gmail, ensure you're using an App Password
- Check the logs for SMTP errors

### Scheduler Not Running
- Ensure `scheduler_config.json` has `"enabled": true`
- Check `scheduler.log` for any errors
- Verify the time format is correct (HH:MM)

## Customization

### Adding More Job Types
Edit the `search_params` in `salesforce_job_scraper.py`:
```python
self.search_params = {
    "search": "",
    "team": "Software+Engineering",
    "jobtype": "New+Grads",  # Change this
    "pagesize": "20"
}
```

### Changing Notification Format
Modify the `send_notification` method in `salesforce_job_scraper.py` to customize the output format.

## Legal Notice

This scraper is for personal use only. Please respect Salesforce's robots.txt and terms of service. Consider adding delays between requests to be respectful to their servers.

## License

This project is for educational and personal use only.

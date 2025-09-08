# Setting Up GitHub Actions for Salesforce Job Scraper

This guide will help you set up your Salesforce job scraper to run automatically on GitHub Actions (completely free!).

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right and select "New repository"
3. Name it something like `salesforce-job-scraper`
4. Make it **Public** (required for free GitHub Actions)
5. Don't initialize with README (we already have files)
6. Click "Create repository"

## Step 2: Upload Your Code

1. In your terminal, navigate to your project folder:
   ```bash
   cd /Users/angela/salesforce-job-scraper
   ```

2. Initialize git and push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Salesforce job scraper"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/salesforce-job-scraper.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Configure Email Secrets

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret** and add these secrets:

   - **FROM_EMAIL**: Your email address (e.g., `your-email@gmail.com`)
   - **TO_EMAIL**: Where to send notifications (e.g., `your-email@gmail.com`)
   - **SMTP_SERVER**: `smtp.gmail.com` (for Gmail)
   - **SMTP_PORT**: `587`
   - **EMAIL_PASSWORD**: Your Gmail App Password (not your regular password!)

### Getting Gmail App Password:
1. Go to [Google Account settings](https://myaccount.google.com/)
2. Security → 2-Step Verification (enable if not already)
3. App passwords → Generate app password
4. Use this password in the EMAIL_PASSWORD secret

## Step 4: Test the Workflow

1. Go to the **Actions** tab in your repository
2. You should see "Salesforce Job Scraper" workflow
3. Click on it and then "Run workflow" to test manually
4. Check the logs to see if it works

## Step 5: Schedule Times

The workflow is currently set to run at:
- 9:00 AM UTC
- 3:00 PM UTC  
- 9:00 PM UTC

To change these times, edit `.github/workflows/salesforce-scraper.yml` and modify the cron schedule:

```yaml
- cron: '0 9,15,21 * * *'  # 9 AM, 3 PM, 9 PM UTC
```

Cron format: `minute hour day month day-of-week`
- `0 9 * * *` = 9:00 AM UTC daily
- `0 9,15,21 * * *` = 9 AM, 3 PM, 9 PM UTC daily

## Benefits

✅ **Completely free** (no cost at all)
✅ **Runs automatically** without your laptop being on
✅ **Email notifications** when new jobs are found
✅ **Logs and database** are preserved between runs
✅ **Manual trigger** available for testing
✅ **No server management** required

## Monitoring

- Check the **Actions** tab to see run history
- View logs for each run to debug issues
- Download artifacts (logs/database) if needed

## Troubleshooting

**Workflow not running:**
- Make sure repository is public
- Check that secrets are set correctly
- Verify cron schedule syntax

**Email not working:**
- Double-check email secrets
- Ensure Gmail App Password is correct
- Check workflow logs for SMTP errors

**No jobs found:**
- Check the scraper logs in Actions
- The scraper might need updates if Salesforce changes their site

That's it! Your scraper will now run automatically on GitHub's servers. 🎉

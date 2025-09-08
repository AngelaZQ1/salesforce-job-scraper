#!/bin/bash

# Salesforce Job Scraper Startup Script

echo "🚀 Starting Salesforce New Grad Job Scraper..."
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import requests, bs4, schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing required packages..."
    pip3 install -r requirements.txt
fi

# Create email config if it doesn't exist
if [ ! -f "email_config.json" ]; then
    echo "📧 Email config not found. Creating from template..."
    cp email_config.json.example email_config.json
    echo "⚠️  Please edit email_config.json with your email settings"
fi

echo "✅ Setup complete!"
echo ""
echo "Choose an option:"
echo "1. Run scraper once (manual)"
echo "2. Start daily scheduler"
echo "3. Test scraper"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🔍 Running scraper once..."
        python3 salesforce_job_scraper.py
        ;;
    2)
        echo "⏰ Starting daily scheduler..."
        echo "Press Ctrl+C to stop"
        python3 scheduler.py
        ;;
    3)
        echo "🧪 Testing scraper..."
        python3 test_scraper.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Quick Start Guide - YouTube Profile Scraper

## Installation (One-Time Setup)

```bash
# 1. Install Python packages
pip3 install -r requirements.txt

# 2. Install browsers
python3 -m playwright install firefox chromium
```

## Basic Usage

### Scrape ONE channel:
```bash
python3 main.py --url "https://www.youtube.com/@NetworkChuck"
```

### Scrape MULTIPLE channels:
```bash
# 1. Create/edit channels.txt with your URLs (one per line)
# 2. Run:
python3 main.py --input channels.txt --output my_results
```

## Files You'll Get

- `my_results.json` - Complete data in JSON format
- `my_results.csv` - Spreadsheet-friendly CSV format

## What Gets Scraped

✅ Channel name
✅ Subscribers count
✅ Video count  
✅ Total views
✅ Join date
✅ Country/Location
✅ Social media links (Twitter, Instagram, etc.)
⚠️  Email (only if logged in to YouTube)

## Options

```bash
# Run without browser window (faster)
python3 main.py --input channels.txt --headless

# Save to specific folder
python3 main.py --input channels.txt --output-dir ./results

# Show detailed errors
python3 main.py --input channels.txt --debug
```

## Your 2Captcha Balance

- Current: **$10.00**
- Cost per email: ~$0.001
- This gives you ~3,000-10,000 email extractions

## Notes

- Browser window will open (you'll see it scraping)
- Takes ~5-10 seconds per channel
- Data saves after EACH channel (safe if interrupted)
- Email extraction requires YouTube login

## Help

For detailed documentation, see `README.md`

For implementation details, see `IMPLEMENTATION_SUMMARY.md`


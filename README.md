# YouTube Profile Scraper

A Python-based scraper to extract YouTube creator profile information including hidden email addresses (with reCAPTCHA solving).

## Features

- ✅ Extracts comprehensive channel information (subscribers, videos, views, join date, location)
- ✅ Retrieves social media links (Twitter, Instagram, Twitch, TikTok, Facebook, etc.)
- ✅ Handles hidden email addresses with automatic reCAPTCHA solving via 2Captcha
- ✅ Batch processing support for multiple channels
- ✅ Exports data to both JSON and CSV formats
- ✅ Automatic consent dialog handling
- ✅ Rate limiting and error handling
- ✅ Incremental saves (data saved after each channel)

## Setup

### 1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

### 2. Install Playwright browsers:
```bash
python3 -m playwright install firefox chromium
```

### 3. Configure 2Captcha API key:

The 2Captcha API key is already configured in `config.py`. You can change it by editing the file:

```python
# config.py
CAPTCHA_API_KEY = "your_api_key_here"
```

Your current balance: **$10.00**

## Usage

### Scrape a single channel:
```bash
python3 main.py --url "https://www.youtube.com/@NetworkChuck"
```

### Scrape multiple channels from a file:

1. Create a `channels.txt` file with one URL per line:
```
https://www.youtube.com/@NetworkChuck
https://www.youtube.com/@ThePrimeagen
https://www.youtube.com/@Fireship
```

2. Run the scraper:
```bash
python3 main.py --input channels.txt --output results
```

### Advanced Options:

```bash
# Run in headless mode (no browser window)
python3 main.py --input channels.txt --headless

# Specify output directory
python3 main.py --input channels.txt --output-dir ./results

# Custom output filename
python3 main.py --input channels.txt --output my_channels

# Debug mode
python3 main.py --input channels.txt --debug
```

## Output

The scraper creates two files:
- `results.json` - All scraped data in JSON format
- `results.csv` - All scraped data in CSV format (flat structure)

### Sample Output:

```json
{
  "channel_url": "https://www.youtube.com/@NetworkChuck",
  "channel_handle": "NetworkChuck",
  "channel_name": "NetworkChuck",
  "subscribers": "5.04M subscribers",
  "video_count": "553 videos",
  "total_views": "367,524,086 views",
  "joined_date": "Joined Apr 27, 2014",
  "country": "United States",
  "description": "Welcome to NetworkChuck!",
  "social_links": {
    "Twitter": "https://twitter.com/networkchuck",
    "Instagram": "https://instagram.com/networkchuck",
    "Twitch": "https://twitch.tv/networkchuck"
  },
  "email": "chuck@networkchuck.com",
  "scraped_at": "2024-12-28 10:00:00"
}
```

## Email Extraction

### Important Notes:
1. **Login Required**: To view channel emails, you must be logged in to YouTube
2. **Not All Channels Have Public Emails**: Many creators don't provide email addresses
3. **reCAPTCHA Solving**: When an email is available, YouTube shows a reCAPTCHA which is automatically solved using 2Captcha

### Cost:
- 2Captcha charges approximately $1-3 per 1000 captcha solves
- For 100 profiles with emails: expect ~$0.10-0.30 in costs
- Your current balance is sufficient for ~3,000-10,000 captcha solves

### Without Login:
If you run the scraper without being logged in to YouTube, you'll see:
```
⚠ Email requires sign-in (not logged in to YouTube)
```

The scraper will still collect all other channel information.

## Project Structure

```
youtube scraper/
├── main.py                 # CLI interface and batch processing
├── scraper.py             # Core scraper logic
├── captcha_solver.py      # 2Captcha API integration
├── session_manager.py     # YouTube session/cookie management
├── data_exporter.py       # JSON and CSV export
├── config.py              # Configuration settings
├── channels.txt           # Sample input file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Configuration

Edit `config.py` to customize:

- `CAPTCHA_API_KEY` - Your 2Captcha API key
- `DELAY_BETWEEN_PROFILES` - Seconds to wait between scraping channels (default: 3)
- `CAPTCHA_TIMEOUT` - Max seconds to wait for captcha solution (default: 120)
- `HEADLESS` - Run browser in headless mode (default: False)

## Troubleshooting

### Browser crashes immediately
- The scraper automatically falls back from Chromium to Firefox if there are issues
- Try running with `--no-headless` to see what's happening

### Consent dialog blocks access
- The scraper automatically handles YouTube consent dialogs
- If it fails, try running with `--no-headless` to manually accept

### Captcha solving fails
- Check your 2Captcha balance at https://2captcha.com
- Verify your API key in `config.py`
- Increase `CAPTCHA_TIMEOUT` if needed

### Session expires
- Run `python3 session_manager.py` to create a new logged-in session
- Note: Session management is implemented but requires manual browser login

## Testing

The scraper has been tested successfully on:
- ✅ NetworkChuck (@NetworkChuck)
- ✅ ThePrimeagen (@ThePrimeagen)
- ✅ Fireship (@Fireship)

All channel information was successfully extracted, including stats and social media links.

## Limitations

1. **Email Access**: Requires YouTube login to view email addresses
2. **Rate Limiting**: YouTube may block excessive requests. Use `DELAY_BETWEEN_PROFILES` to avoid issues.
3. **Dynamic Content**: YouTube's page structure may change, requiring selector updates
4. **Browser Compatibility**: Works best with Firefox on macOS

## License

This tool is for educational purposes only. Be respectful of YouTube's Terms of Service and use responsibly.


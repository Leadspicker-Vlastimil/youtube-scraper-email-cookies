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

### 4. **IMPORTANT: Import Your YouTube Cookies** (Required for Email Extraction)

To extract email addresses, you need to be logged in to YouTube. Import your browser cookies:

#### Option A: Use the provided cookie importer (Recommended)

Your cookies are already imported! The file `youtube_session.json` contains your authenticated session.

#### Option B: Import from browser manually

1. Export cookies from your browser using a cookie export extension
2. Save them to a JSON file
3. Run: `python3 import_cookies.py` (edit the script with your cookies)

**Your cookies expire on:** January 25, 2027

✅ **You're all set!** The scraper will now be able to access email addresses.

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

### ✅ Working with Authentication!

With your imported cookies, the scraper can now extract email addresses from channels that have them public.

**Test Results:**
- NetworkChuck: ✅ `chuck@networkchuck.com` extracted successfully!

### How It Works:
1. Scraper loads your YouTube session cookies
2. Navigates to channel About page while authenticated
3. If email is available, it's already visible (no captcha needed in most cases)
4. If captcha appears, it's automatically solved using 2Captcha
5. Email is extracted and saved to output files

### Important Notes:
1. **Cookies Valid Until:** January 25, 2027
2. **Not All Channels Have Public Emails**: Many creators don't provide email addresses
3. **reCAPTCHA May Appear**: When it does, 2Captcha automatically solves it ($0.001-0.003 per solve)

### Without Cookies:
If cookies expire or you run without authentication, you'll see:
```
⚠ Email requires sign-in (not logged in to YouTube)
```

Simply re-import your cookies using the import_cookies.py script.

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


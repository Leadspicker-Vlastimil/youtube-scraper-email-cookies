"""Configuration settings for YouTube scraper."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 2Captcha API settings
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY", "2f304e00e6c4e41e68ebf866e6b014c8")
CAPTCHA_TIMEOUT = int(os.getenv("CAPTCHA_TIMEOUT", "120"))

# Session settings
SESSION_FILE = "youtube_session.json"

# Scraper settings
DELAY_BETWEEN_PROFILES = int(os.getenv("DELAY_BETWEEN_PROFILES", "3"))
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"

# Browser settings
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Validation
if not CAPTCHA_API_KEY:
    print("WARNING: CAPTCHA_API_KEY not set in .env file")


"""
Cookie importer - Convert browser cookies to Playwright format.

This script converts cookies from browser extension format to Playwright's storage state format.
"""
import json
import time
from datetime import datetime


def convert_cookies_to_playwright(browser_cookies):
    """
    Convert browser extension cookies to Playwright storage state format.
    
    Args:
        browser_cookies: List of cookies in browser extension format
        
    Returns:
        Dictionary in Playwright storage state format
    """
    playwright_cookies = []
    
    for cookie in browser_cookies:
        # Convert to Playwright format
        pw_cookie = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie["path"],
            "secure": cookie["secure"],
            "httpOnly": cookie["httpOnly"],
        }
        
        # Add expiration if present
        if "expirationDate" in cookie and cookie["expirationDate"]:
            pw_cookie["expires"] = int(cookie["expirationDate"])
        
        # Add sameSite if present
        if "sameSite" in cookie and cookie["sameSite"]:
            sameSite = cookie["sameSite"]
            if sameSite == "no_restriction":
                sameSite = "None"
            elif sameSite:
                sameSite = sameSite.capitalize()
            pw_cookie["sameSite"] = sameSite
        
        playwright_cookies.append(pw_cookie)
    
    # Create Playwright storage state format
    storage_state = {
        "cookies": playwright_cookies,
        "origins": []
    }
    
    return storage_state


def save_cookies_to_file(browser_cookies, output_file="youtube_session.json"):
    """
    Convert and save cookies to Playwright format.
    
    Args:
        browser_cookies: List of cookies in browser extension format
        output_file: Path to save the converted cookies
    """
    storage_state = convert_cookies_to_playwright(browser_cookies)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(storage_state, f, indent=2)
    
    print(f"✓ Cookies saved to {output_file}")
    print(f"  Total cookies: {len(storage_state['cookies'])}")
    
    # Check cookie expiration
    now = time.time()
    expired = 0
    valid = 0
    
    for cookie in storage_state['cookies']:
        if 'expires' in cookie:
            if cookie['expires'] < now:
                expired += 1
            else:
                valid += 1
                # Show when cookies expire
                expiry_date = datetime.fromtimestamp(cookie['expires'])
                if cookie['name'] in ['SID', 'HSID', 'SSID']:
                    print(f"  {cookie['name']} expires: {expiry_date.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"  Valid cookies: {valid}")
    if expired > 0:
        print(f"  ⚠ Expired cookies: {expired}")
    
    return output_file


def import_cookies_from_json(json_file):
    """
    Import cookies from a JSON file and convert to Playwright format.
    
    Args:
        json_file: Path to JSON file with browser cookies
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        browser_cookies = json.load(f)
    
    return save_cookies_to_file(browser_cookies)


if __name__ == "__main__":
    # Your YouTube cookies
    youtube_cookies = [
        {
            "domain": ".youtube.com",
            "expirationDate": 1801086567.389103,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-YEC",
            "path": "/",
            "sameSite": "lax",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "CgthSXhDOVdIRXRHayjNzcbKBjInCgJDWhIhEh0SGwsMDg8QERITFBUWFxgZGhscHR4fICEiIyQlJiBr"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.788056,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-3PSID",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "g.a0004gj39-joHkXDikxhhIvNGtqUGP_i51r2pPE5-OVHK0CuCe-GoS8z9KVKrkrqCPWMBeorNQACgYKAdISARASFQHGX2MiBdnFyxqQE_UQ2CUEOvSZchoVAUF8yKqbgHvCJ9gAXTABKQqkTYhB0076"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1798496377.518102,
            "hostOnly": False,
            "httpOnly": False,
            "name": "SIDCC",
            "path": "/",
            "sameSite": None,
            "secure": False,
            "session": False,
            "storeId": None,
            "value": "AKEyXzU_MEOGnNBzh7rlDEXIKgIPXrIlRhrF1--Hpog6OrpVSwECh7-RWRY5gGOeiBqS0WZ-rA"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787926,
            "hostOnly": False,
            "httpOnly": False,
            "name": "SID",
            "path": "/",
            "sameSite": None,
            "secure": False,
            "session": False,
            "storeId": None,
            "value": "g.a0004gj39-joHkXDikxhhIvNGtqUGP_i51r2pPE5-OVHK0CuCe-G93wVRqlt_6RFwHjKyEsLUAACgYKASgSARASFQHGX2Mi-XAztF8sMFIJdBz5b2vfWRoVAUF8yKpJ8-WQgDrK6UEcoIajou9A0076"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1798496377.517877,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-1PSIDTS",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "sidts-CjQBflaCdUbOCBmNoRTeIdgw5Ywi4e9efF0iMZPX0orWL69c939pKbPmbsR7OoPMX2fV2kIdEAA"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787747,
            "hostOnly": False,
            "httpOnly": False,
            "name": "SAPISID",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "rNlnZUugyhr9p_3i/AJR5_dKpnrbSof2yl"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1798496377.518146,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-1PSIDCC",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "AKEyXzVQR0qXJPGTOlIED8DqQM_HHMQTk53BqKJuRb3bOYN35IKZkhvAcITYKb3yKBSsxkglEZg"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787578,
            "hostOnly": False,
            "httpOnly": True,
            "name": "SSID",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "AIqKRHW9keiyDjH1U"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787805,
            "hostOnly": False,
            "httpOnly": False,
            "name": "__Secure-1PAPISID",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "rNlnZUugyhr9p_3i/AJR5_dKpnrbSof2yl"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787994,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-1PSID",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "g.a0004gj39-joHkXDikxhhIvNGtqUGP_i51r2pPE5-OVHK0CuCe-Gn-EB3vm5qGCQrHu24JLhDQACgYKAd4SARASFQHGX2Mi4iu6YgprL1Rl9bDSQwuHtBoVAUF8yKoN5QpRGdx2WESlergAXFVs0076"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787867,
            "hostOnly": False,
            "httpOnly": False,
            "name": "__Secure-3PAPISID",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "rNlnZUugyhr9p_3i/AJR5_dKpnrbSof2yl"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1798496377.51819,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-3PSIDCC",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "AKEyXzX-nhI0h24fU5LZqtmjdV1Fm2bbpi3XqChrvk-cySkrEWuExqdDtuLjv94-8h32iLjw3g"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1798496377.51805,
            "hostOnly": False,
            "httpOnly": True,
            "name": "__Secure-3PSIDTS",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "sidts-CjQBflaCdUbOCBmNoRTeIdgw5Ywi4e9efF0iMZPX0orWL69c939pKbPmbsR7OoPMX2fV2kIdEAA"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787682,
            "hostOnly": False,
            "httpOnly": False,
            "name": "APISID",
            "path": "/",
            "sameSite": None,
            "secure": False,
            "session": False,
            "storeId": None,
            "value": "2IxxKVGHs1EP4iq9/A7jEEeg_lW3EWYRu3"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800907829.787442,
            "hostOnly": False,
            "httpOnly": True,
            "name": "HSID",
            "path": "/",
            "sameSite": None,
            "secure": False,
            "session": False,
            "storeId": None,
            "value": "AKTN27H8Wm1jk-p-4"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1795296573.401162,
            "hostOnly": False,
            "httpOnly": True,
            "name": "LOGIN_INFO",
            "path": "/",
            "sameSite": "no_restriction",
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "AFmmF2swRQIhAM6MkC8ZEKfqzN-a4QNhM-kzHajLGE4UFwZsMLDVoyZ3AiAiq7DGWd-bghEGM31pY_3MsDN0r-bTwOSPlSJUDYopew:QUQ3MjNmeUxpU09RTlJSSG9xVV92TkJHeWJnX3N4SERTbFBmenZLSXF3SkxzeTh1WTlaVUZMamNGZWh0c203LXNQTkhIcUtFQXFOSjNaYUxOSk1SZXhjR294UmpLcDUtNzN4djVMam1sWGdFMlRrZWZXbWZOdkE2a200MDd2aHE4akdUeEdiRWhxTnEzVnA4UzNlY3ctNnowbXFtVEEyWmRB"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1801518798.089797,
            "hostOnly": False,
            "httpOnly": False,
            "name": "PREF",
            "path": "/",
            "sameSite": None,
            "secure": True,
            "session": False,
            "storeId": None,
            "value": "tz=Europe.Prague&f5=30000&f7=100&f4=4000000"
        }
    ]
    
    print("Converting YouTube cookies to Playwright format...")
    save_cookies_to_file(youtube_cookies)
    print("\n✓ Done! You can now use the scraper with authentication.")
    print("\nUsage:")
    print("  python3 main.py --url 'https://www.youtube.com/@NetworkChuck'")


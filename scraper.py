"""YouTube profile scraper core functionality."""
import time
import re
from typing import Dict, Optional, Any
from playwright.sync_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout
from session_manager import SessionManager
from captcha_solver import CaptchaSolver
import config


class YouTubeScraper:
    """Scrapes YouTube channel profile information."""
    
    def __init__(self, session_manager: SessionManager = None, captcha_solver: CaptchaSolver = None):
        """
        Initialize the scraper.
        
        Args:
            session_manager: SessionManager instance. If None, creates a new one.
            captcha_solver: CaptchaSolver instance. If None, creates a new one.
        """
        self.session_manager = session_manager or SessionManager()
        self.captcha_solver = captcha_solver or CaptchaSolver()
        self.context = None
    
    def start(self, headless: bool = None, use_session: bool = True):
        """
        Start the browser and create context.
        
        Args:
            headless: Run in headless mode
            use_session: Use saved cookies for authentication (default: True)
        """
        _, self.context = self.session_manager.start_browser(headless=headless, use_session=use_session)
    
    def close(self):
        """Close the browser and clean up."""
        self.session_manager.close()
    
    def scrape_channel(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a YouTube channel profile.
        
        Args:
            channel_url: URL of the YouTube channel (e.g., https://www.youtube.com/@NetworkChuck)
            
        Returns:
            Dictionary with channel data, or None if scraping failed
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
        
        print(f"\n{'='*60}")
        print(f"Scraping: {channel_url}")
        print(f"{'='*60}\n")
        
        page = self.context.new_page()
        
        try:
            # Navigate to channel About page (not featured page)
            print("1. Navigating to channel About page...")
            
            # Convert URL to about page if needed
            about_url = channel_url.rstrip('/') + '/about'
            if '/featured' in about_url:
                about_url = about_url.replace('/featured', '/about')
            
            page.goto(about_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Handle YouTube consent dialog if it appears
            self._handle_consent_dialog(page)
            
            # Initialize data dictionary
            data = {
                "channel_url": channel_url,
                "channel_handle": self._extract_handle_from_url(channel_url),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Extract information from About page (no need to click 'more' button)
            print("2. Extracting channel information from About page...")
            channel_info = self._extract_about_page_info(page)
            data.update(channel_info)
            
            # Try to get email address
            print("3. Attempting to extract email...")
            email = self._extract_email_from_about(page)
            data["email"] = email
            
            print(f"\n✓ Successfully scraped channel: {data.get('channel_name', 'Unknown')}")
            
            return data
            
        except Exception as e:
            print(f"✗ Error scraping channel: {e}")
            import traceback
            traceback.print_exc()
            return data
            
        finally:
            page.close()
    
    def _extract_handle_from_url(self, url: str) -> str:
        """Extract channel handle from URL."""
        match = re.search(r'/@([^/]+)', url)
        return match.group(1) if match else ""
    
    def _handle_consent_dialog(self, page: Page):
        """Handle YouTube consent/cookie dialog if it appears."""
        try:
            # Check if we're on a consent page
            if 'consent.youtube.com' in page.url or 'Before you continue' in page.content():
                print("  Handling consent dialog...")
                
                # Try to click "Accept all" or "Reject all" button
                accept_buttons = [
                    "button:has-text('Accept all')",
                    "button:has-text('Reject all')",
                    "[aria-label*='Accept']",
                    "//button[contains(text(), 'Accept')]"
                ]
                
                for selector in accept_buttons:
                    try:
                        if selector.startswith('//'):
                            button = page.locator(f"xpath={selector}").first
                        else:
                            button = page.locator(selector).first
                        
                        if button.count() > 0:
                            button.click(timeout=5000)
                            page.wait_for_timeout(2000)
                            print("  ✓ Consent dialog handled")
                            return
                    except:
                        continue
                
                print("  ⚠ Could not handle consent dialog automatically")
        except:
            pass  # No consent dialog or already handled
    
    def _extract_about_page_info(self, page: Page) -> Dict[str, Any]:
        """
        Extract channel information from the About page.
        
        Returns:
            Dictionary with channel info
        """
        info = {}
        
        try:
            # Extract channel name from page title or header
            try:
                # Try from page title first
                title = page.title()
                if ' - YouTube' in title:
                    name = title.replace(' - YouTube', '').strip()
                    info["channel_name"] = name
                    print(f"  Name: {info['channel_name']}")
            except:
                info["channel_name"] = ""
            
            # Extract stats from the About page table
            # The info is displayed in rows with specific text patterns
            
            # Wait a bit more for stats to load
            page.wait_for_timeout(2000)
            
            # Get all text content and use regex to extract info
            page_text = page.content()
            
            # Try to extract subscribers with regex
            if not info.get("subscribers"):
                subs_patterns = [
                    r'([\d,.]+[KkMm]?\s*subscribers?)',
                    r'(\d+[\d,.]*[KkMm]?\s*subscribers?)'
                ]
                for pattern in subs_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        info["subscribers"] = match.group(1)
                        print(f"  Subscribers: {info['subscribers']}")
                        break
            
            # Try to extract video count
            if not info.get("video_count"):
                video_patterns = [
                    r'(\d+[\d,]*\s*videos?)',
                    r'([\d,.]+\s*videos?)'
                ]
                for pattern in video_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        info["video_count"] = match.group(1)
                        print(f"  Videos: {info['video_count']}")
                        break
            
            # Try to extract views
            if not info.get("total_views"):
                views_patterns = [
                    r'([\d,]+\s*views?)',
                    r'(\d+[\d,]*\s*views?)'
                ]
                for pattern in views_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        info["total_views"] = match.group(1)
                        print(f"  Views: {info['total_views']}")
                        break
            
            # Try to extract join date
            if not info.get("joined_date"):
                joined_patterns = [
                    r'(Joined\s+\w+\s+\d+,?\s*\d{4})',
                    r'(Joined.*?\d{4})'
                ]
                for pattern in joined_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        info["joined_date"] = match.group(1)
                        print(f"  {info['joined_date']}")
                        break
            
            # Try to extract country from common locations
            if not info.get("country"):
                countries = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France', 'Spain', 'Italy', 'Netherlands', 'Japan', 'India', 'Brazil']
                for country in countries:
                    if country in page_text:
                        info["country"] = country
                        print(f"  Location: {country}")
                        break
            
            # Set default empty values for missing fields
            if "subscribers" not in info:
                info["subscribers"] = ""
            if "video_count" not in info:
                info["video_count"] = ""
            if "total_views" not in info:
                info["total_views"] = ""
            if "joined_date" not in info:
                info["joined_date"] = ""
            if "country" not in info:
                info["country"] = ""
            
            # Extract description
            try:
                # Look for description in the About page
                desc_container = page.locator('#description-container, #description').first
                if desc_container.count() > 0:
                    desc = desc_container.inner_text(timeout=2000)
                    info["description"] = desc.strip()[:500]  # Limit to 500 chars
                else:
                    info["description"] = ""
            except:
                info["description"] = ""
            
            # Extract social media links
            info["social_links"] = {}
            try:
                # Look for links in the channel links section
                links = page.locator('a[href]').all()
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        if href and any(domain in href.lower() for domain in ['twitter', 'instagram', 'twitch', 'facebook', 'tiktok', 'linkedin']):
                            # Get the link text or aria-label
                            try:
                                text = link.inner_text(timeout=500)
                                if not text:
                                    text = link.get_attribute('aria-label') or href
                                text = text.strip()
                                if text and len(text) < 100:  # Reasonable label length
                                    info["social_links"][text] = href
                            except:
                                pass
                    except:
                        continue
            except:
                pass
            
        except Exception as e:
            print(f"  ⚠ Error extracting channel info: {e}")
        
        return info
    
    def _click_more_button(self, page: Page) -> bool:
        """
        Click the 'more' button to expand channel description.
        
        Returns:
            True if successful
        """
        try:
            # Look for the "more" button/link in the channel header description
            # YouTube uses various selectors, try multiple approaches
            selectors = [
                "button[aria-label*='more']",
                "tp-yt-paper-button#expand",
                "#description-container button",
                "//button[contains(text(), 'more')]",
                "//span[contains(text(), 'more')]/..",
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        # XPath selector
                        button = page.locator(f"xpath={selector}").first
                    else:
                        button = page.locator(selector).first
                    
                    if button.count() > 0 and button.is_visible(timeout=2000):
                        button.click(timeout=5000)
                        page.wait_for_timeout(1000)
                        print("  ✓ Clicked 'more' button")
                        
                        # Wait for modal/popup to appear
                        page.wait_for_selector('tp-yt-paper-dialog', timeout=5000)
                        return True
                except:
                    continue
            
            print("  ⚠ 'More' button not found, trying alternative...")
            
            # Alternative: Look for channel name/avatar to click
            try:
                # Click on channel name or avatar which also opens the modal
                channel_name = page.locator('#channel-name a').first
                if channel_name.count() > 0:
                    channel_name.click()
                    page.wait_for_timeout(1000)
                    page.wait_for_selector('tp-yt-paper-dialog', timeout=5000)
                    print("  ✓ Opened channel info via channel name")
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"  ✗ Error clicking more button: {e}")
            return False
    
    def _extract_channel_info(self, page: Page) -> Dict[str, Any]:
        """
        Extract channel information from the open modal.
        
        Returns:
            Dictionary with channel info
        """
        info = {}
        
        try:
            # Wait for modal to be visible
            page.wait_for_selector('tp-yt-paper-dialog', timeout=5000)
            
            # Extract channel name
            try:
                name = page.locator('#channel-title').first.inner_text(timeout=2000)
                info["channel_name"] = name.strip()
                print(f"  Name: {info['channel_name']}")
            except:
                info["channel_name"] = ""
            
            # Extract subscriber count
            try:
                # Look for subscriber count in the modal
                subs_selectors = [
                    "#subscriber-count",
                    "yt-formatted-string:has-text('subscriber')",
                    "[id='subscriber-count']"
                ]
                for selector in subs_selectors:
                    try:
                        subs = page.locator(selector).first.inner_text(timeout=2000)
                        info["subscribers"] = subs.strip()
                        print(f"  Subscribers: {info['subscribers']}")
                        break
                    except:
                        continue
                if "subscribers" not in info:
                    info["subscribers"] = ""
            except:
                info["subscribers"] = ""
            
            # Extract video count
            try:
                videos_selectors = [
                    "yt-formatted-string:has-text('video')",
                    "#videos-count"
                ]
                for selector in videos_selectors:
                    try:
                        videos = page.locator(selector).first.inner_text(timeout=2000)
                        info["video_count"] = videos.strip()
                        print(f"  Videos: {info['video_count']}")
                        break
                    except:
                        continue
                if "video_count" not in info:
                    info["video_count"] = ""
            except:
                info["video_count"] = ""
            
            # Extract total views
            try:
                views_selectors = [
                    "yt-formatted-string:has-text('views')",
                    "#view-count"
                ]
                for selector in views_selectors:
                    try:
                        views = page.locator(selector).first.inner_text(timeout=2000)
                        info["total_views"] = views.strip()
                        print(f"  Views: {info['total_views']}")
                        break
                    except:
                        continue
                if "total_views" not in info:
                    info["total_views"] = ""
            except:
                info["total_views"] = ""
            
            # Extract join date
            try:
                joined_selectors = [
                    "yt-formatted-string:has-text('Joined')",
                    "#joined-date"
                ]
                for selector in joined_selectors:
                    try:
                        joined = page.locator(selector).first.inner_text(timeout=2000)
                        info["joined_date"] = joined.strip()
                        print(f"  {info['joined_date']}")
                        break
                    except:
                        continue
                if "joined_date" not in info:
                    info["joined_date"] = ""
            except:
                info["joined_date"] = ""
            
            # Extract country/location
            try:
                country_selectors = [
                    "#country",
                    "yt-formatted-string:has-text('United States')",  # Common, but varies
                ]
                for selector in country_selectors:
                    try:
                        country = page.locator(selector).first.inner_text(timeout=2000)
                        info["country"] = country.strip()
                        print(f"  Location: {info['country']}")
                        break
                    except:
                        continue
                if "country" not in info:
                    info["country"] = ""
            except:
                info["country"] = ""
            
            # Extract description
            try:
                desc_selectors = [
                    "#description-container",
                    "#description"
                ]
                for selector in desc_selectors:
                    try:
                        desc = page.locator(selector).first.inner_text(timeout=2000)
                        info["description"] = desc.strip()[:500]  # Limit to 500 chars
                        break
                    except:
                        continue
                if "description" not in info:
                    info["description"] = ""
            except:
                info["description"] = ""
            
            # Extract social media links
            info["social_links"] = {}
            try:
                links = page.locator('tp-yt-paper-dialog a[href]').all()
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        text = link.inner_text()
                        if href and any(domain in href.lower() for domain in ['twitter', 'instagram', 'twitch', 'facebook', 'tiktok']):
                            info["social_links"][text or href] = href
                    except:
                        continue
            except:
                pass
            
        except Exception as e:
            print(f"  ⚠ Error extracting channel info: {e}")
        
        return info
    
    def _extract_email_from_about(self, page: Page) -> Optional[str]:
        """
        Extract email address from About page (requires solving captcha if present).
        
        Returns:
            Email address or None
        """
        try:
            # Wait a bit for page to fully load
            page.wait_for_timeout(2000)
            
            # Look for "View email address" link/button or "Sign in to see email"
            page_text = page.inner_text('body')
            
            # Check for sign-in requirement (more specific check)
            if 'Sign in to see email address' in page_text:
                print("  ⚠ Email requires sign-in (not logged in to YouTube)")
                return None
            
            # First check if email is already visible (happens after authentication sometimes)
            page_content = page.content()
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_content)
            if email_match:
                email = email_match.group(0)
                # Filter out common false positives
                if not any(ex in email.lower() for ex in ['noreply@', 'example@', 'test@', '@youtube', '@google']):
                    print(f"  ✓ Email already visible: {email}")
                    return email
            
            # Look for "View email address" button/link - try multiple selectors
            print("  Looking for 'View email address' button...")
            email_selectors = [
                "text=/View email address/i",
                "button:has-text('View email')",
                "a:has-text('View email')",
                "[aria-label*='email' i]",
                "yt-button-renderer:has-text('View email')",
                "a.yt-simple-endpoint:has-text('email')",
            ]
            
            email_button = None
            for selector in email_selectors:
                try:
                    buttons = page.locator(selector).all()
                    for button in buttons:
                        try:
                            if button.is_visible(timeout=1000):
                                button_text = button.inner_text(timeout=1000).lower()
                                if 'view' in button_text and 'email' in button_text:
                                    email_button = button
                                    print(f"  ✓ Found 'View email address' button")
                                    break
                        except:
                            continue
                    if email_button:
                        break
                except:
                    continue
            
            if not email_button:
                print("  ⚠ 'View email address' button not found (channel may not have public email)")
                return None
            
            # Click the button
            print("  Clicking 'View email address' button...")
            try:
                email_button.click(timeout=5000)
                print("  Button clicked, waiting for response...")
                page.wait_for_timeout(5000)  # Wait longer for content to load/modal to appear
            except Exception as e:
                print(f"  ✗ Error clicking button: {e}")
                return None
            
            # Check if reCAPTCHA appeared
            print("  Checking for reCAPTCHA...")
            page.wait_for_timeout(2000)  # Give time for captcha to load if it will
            
            if self._has_recaptcha(page):
                print("  ✓ reCAPTCHA detected, solving...")
                success = self._solve_recaptcha(page)
                if not success:
                    print("  ✗ Failed to solve reCAPTCHA")
                    return None
                print("  ✓ reCAPTCHA solved, waiting for email...")
                page.wait_for_timeout(5000)
            else:
                print("  No reCAPTCHA detected, email should be visible now...")
                page.wait_for_timeout(3000)  # Give more time for email to appear
            
            # Extract email from the page (multiple attempts)
            email = self._find_email_on_page(page)
            
            if email:
                print(f"  ✓ Email extracted: {email}")
            else:
                print("  ✗ Could not find email on page after clicking button")
                # Debug: save page content
                try:
                    page_text_after = page.inner_text('body')
                    if 'email' in page_text_after.lower():
                        print(f"  Debug: Page contains 'email' text but couldn't extract address")
                except:
                    pass
            
            return email
            
        except Exception as e:
            print(f"  ✗ Error extracting email: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _has_recaptcha(self, page: Page) -> bool:
        """Check if reCAPTCHA is present on the page."""
        try:
            # Look for reCAPTCHA iframe
            recaptcha_frame = page.frame_locator('iframe[title*="reCAPTCHA"]').first
            return recaptcha_frame.locator('body').count(timeout=3000) > 0
        except:
            return False
    
    def _solve_recaptcha(self, page: Page) -> bool:
        """
        Solve reCAPTCHA using 2Captcha service.
        
        Returns:
            True if successful
        """
        try:
            # Find the reCAPTCHA sitekey
            page_content = page.content()
            sitekey_match = re.search(r'data-sitekey="([^"]+)"', page_content)
            
            if not sitekey_match:
                # Try alternative method
                try:
                    recaptcha_div = page.locator('.g-recaptcha').first
                    sitekey = recaptcha_div.get_attribute('data-sitekey')
                except:
                    print("  ✗ Could not find reCAPTCHA sitekey")
                    return False
            else:
                sitekey = sitekey_match.group(1)
            
            print(f"  Found sitekey: {sitekey[:20]}...")
            
            # Solve captcha using 2Captcha
            solution = self.captcha_solver.solve_recaptcha(sitekey, page.url)
            
            if not solution:
                return False
            
            # Inject the solution
            print("  Injecting solution...")
            inject_script = f"""
            document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
            """
            page.evaluate(inject_script)
            
            # Submit the form or trigger callback
            try:
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']",
                    "button:has-text('Submit')",
                    "input[type='submit']"
                ]
                for selector in submit_selectors:
                    try:
                        submit_btn = page.locator(selector).first
                        if submit_btn.count() > 0:
                            submit_btn.click()
                            break
                    except:
                        continue
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error solving reCAPTCHA: {e}")
            return False
    
    def _find_email_on_page(self, page: Page) -> Optional[str]:
        """Find email address on the page after captcha is solved or button clicked."""
        try:
            # Wait a bit for email to appear
            page.wait_for_timeout(1000)
            
            # Method 1: Try to find email in visible text
            try:
                visible_text = page.inner_text('body')
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                matches = re.findall(email_pattern, visible_text)
                
                if matches:
                    # Filter out common false positives
                    exclude = ['noreply@', 'example@', 'test@', '@youtube', '@google', 'support@']
                    valid_emails = [e for e in matches if not any(ex in e.lower() for ex in exclude)]
                    if valid_emails:
                        return valid_emails[0]
            except Exception as e:
                print(f"  Debug: Error in visible text search: {e}")
            
            # Method 2: Search in page HTML content
            try:
                content = page.content()
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                matches = re.findall(email_pattern, content)
                
                if matches:
                    # Filter out common false positives
                    exclude = ['noreply@', 'example@', 'test@', '@youtube', '@google', 'support@']
                    valid_emails = [e for e in matches if not any(ex in e.lower() for ex in exclude)]
                    if valid_emails:
                        return valid_emails[0]
            except Exception as e:
                print(f"  Debug: Error in HTML content search: {e}")
            
            # Method 3: Look for email in specific containers
            try:
                # Try to find email in modal or dialog
                email_containers = [
                    '[role="dialog"]',
                    '.ytd-about-channel-renderer',
                    '#email',
                    '[id*="email"]',
                ]
                
                for container_selector in email_containers:
                    try:
                        container = page.locator(container_selector).first
                        if container.count() > 0:
                            container_text = container.inner_text(timeout=2000)
                            matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', container_text)
                            if matches:
                                exclude = ['noreply@', 'example@', 'test@', '@youtube', '@google']
                                valid_emails = [e for e in matches if not any(ex in e.lower() for ex in exclude)]
                                if valid_emails:
                                    return valid_emails[0]
                    except:
                        continue
            except Exception as e:
                print(f"  Debug: Error in container search: {e}")
            
            return None
            
        except Exception as e:
            print(f"  Error finding email: {e}")
            return None


def test_scraper():
    """Test the scraper on a sample channel."""
    print("Testing YouTube scraper...\n")
    
    scraper = YouTubeScraper()
    
    try:
        scraper.start(headless=False)
        
        # Test with NetworkChuck channel
        test_url = "https://www.youtube.com/@NetworkChuck"
        data = scraper.scrape_channel(test_url)
        
        if data:
            print("\n" + "="*60)
            print("SCRAPED DATA:")
            print("="*60)
            for key, value in data.items():
                if key != "social_links":
                    print(f"{key}: {value}")
            if "social_links" in data:
                print("social_links:")
                for name, url in data["social_links"].items():
                    print(f"  - {name}: {url}")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    test_scraper()


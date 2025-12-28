"""YouTube session management for maintaining login state."""
import json
import os
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Optional
import config


class SessionManager:
    """Manages YouTube authentication and session persistence."""
    
    def __init__(self, session_file: str = None):
        """
        Initialize session manager.
        
        Args:
            session_file: Path to file for storing session state
        """
        self.session_file = session_file or config.SESSION_FILE
        self.playwright = None
        self.browser = None
        self.context = None
    
    def session_exists(self) -> bool:
        """Check if a saved session file exists."""
        return os.path.exists(self.session_file)
    
    def create_session_interactively(self) -> bool:
        """
        Open a browser for user to manually log in to YouTube.
        Saves the session for future use.
        
        Returns:
            True if session was created successfully
        """
        print("Opening browser for YouTube login...")
        print("Please log in to your YouTube account.")
        
        try:
            with sync_playwright() as p:
                # Try Firefox first (more stable on macOS), fallback to Chromium
                try:
                    browser = p.firefox.launch(headless=False)
                    browser_type = "Firefox"
                except Exception as e:
                    print(f"Firefox failed: {e}, trying Chromium...")
                    browser = p.chromium.launch(headless=False)
                    browser_type = "Chromium"
                
                print(f"Using {browser_type} browser")
                
                context = browser.new_context(
                    user_agent=config.USER_AGENT,
                    viewport={'width': 1280, 'height': 720},
                    locale='en-US'
                )
                
                page = context.new_page()
                
                print("\n" + "="*60)
                print("Browser opened. Please:")
                print("1. Log in to YouTube if not already logged in")
                print("2. Verify you're logged in (check top-right corner)")
                print("3. Press ENTER in this terminal when done")
                print("="*60 + "\n")
                
                # Navigate to YouTube
                page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2000)
                
                # Wait for user to press Enter
                input("Press ENTER after you've logged in...")
                
                # Save the session
                storage_state = context.storage_state()
                with open(self.session_file, 'w') as f:
                    json.dump(storage_state, f, indent=2)
                
                print("Closing browser...")
                page.close()
                context.close()
                browser.close()
                
        except Exception as e:
            print(f"Error during session creation: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        if self.session_exists():
            print(f"\n✓ Session saved to {self.session_file}")
            return True
        else:
            print("\n✗ Failed to save session")
            return False
    
    def start_browser(self, headless: bool = None, use_session: bool = True) -> tuple[Browser, BrowserContext]:
        """
        Start a browser with optional saved session.
        
        Args:
            headless: Whether to run in headless mode. If None, uses config setting.
            use_session: Whether to load saved session. If False, starts fresh browser.
            
        Returns:
            Tuple of (browser, context)
        """
        if headless is None:
            headless = config.HEADLESS
        
        if use_session and not self.session_exists():
            print(f"Warning: No session file found at {self.session_file}")
            print("Starting browser without saved session. You may need to log in manually.")
            use_session = False
        
        self.playwright = sync_playwright().start()
        
        # Try Firefox first (more stable on macOS), fallback to Chromium
        try:
            self.browser = self.playwright.firefox.launch(headless=headless)
        except Exception as e:
            print(f"Firefox failed: {e}, using Chromium...")
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
        
        # Load the saved session if requested
        if use_session:
            with open(self.session_file, 'r') as f:
                storage_state = json.load(f)
            
            self.context = self.browser.new_context(
                storage_state=storage_state,
                user_agent=config.USER_AGENT,
                viewport={'width': 1280, 'height': 720}
            )
        else:
            self.context = self.browser.new_context(
                user_agent=config.USER_AGENT,
                viewport={'width': 1280, 'height': 720},
                locale='en-US'
            )
        
        return self.browser, self.context
    
    def verify_session(self) -> bool:
        """
        Verify that the session is still valid by checking if user is logged in.
        
        Returns:
            True if session is valid
        """
        if not self.context:
            print("No active browser context. Call start_browser() first.")
            return False
        
        page = self.context.new_page()
        try:
            page.goto("https://www.youtube.com", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            
            # Check if user avatar/profile button is present (indicates logged in)
            # This button has id="avatar-btn" when logged in
            avatar_button = page.locator('#avatar-btn').first
            
            if avatar_button.count() > 0:
                print("✓ Session is valid - user is logged in")
                page.close()
                return True
            else:
                print("✗ Session expired - user is not logged in")
                page.close()
                return False
                
        except Exception as e:
            print(f"Error verifying session: {e}")
            page.close()
            return False
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.context:
            self.context.close()
            self.context = None
        
        if self.browser:
            self.browser.close()
            self.browser = None
        
        if self.playwright:
            self.playwright.stop()
            self.playwright = None


def setup_session():
    """Interactive setup to create a new YouTube session."""
    manager = SessionManager()
    
    if manager.session_exists():
        print(f"Session file already exists: {manager.session_file}")
        response = input("Do you want to create a new session? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing session.")
            return
    
    success = manager.create_session_interactively()
    
    if success:
        print("\n✓ Session setup complete!")
        print("You can now run the scraper.")
    else:
        print("\n✗ Session setup failed. Please try again.")


if __name__ == "__main__":
    # Run interactive setup when executed directly
    setup_session()


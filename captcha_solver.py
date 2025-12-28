"""2Captcha API integration for solving reCAPTCHA challenges."""
import time
import requests
from typing import Optional, Dict, Any
import config


class CaptchaSolver:
    """Handles reCAPTCHA solving using 2Captcha API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the captcha solver.
        
        Args:
            api_key: 2Captcha API key. If None, uses value from config.
        """
        self.api_key = api_key or config.CAPTCHA_API_KEY
        if not self.api_key or self.api_key == "your_2captcha_api_key_here":
            raise ValueError("Valid 2Captcha API key required. Set CAPTCHA_API_KEY in .env file.")
        
        self.base_url = "https://2captcha.com"
        self.timeout = config.CAPTCHA_TIMEOUT
    
    def get_balance(self) -> float:
        """
        Get current account balance.
        
        Returns:
            Balance in USD
        """
        try:
            response = requests.get(
                f"{self.base_url}/res.php",
                params={
                    "key": self.api_key,
                    "action": "getbalance",
                    "json": 1
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 1:
                return float(data.get("request", 0))
            else:
                print(f"Warning: Could not get balance: {data.get('request')}")
                return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve a reCAPTCHA challenge.
        
        Args:
            site_key: The reCAPTCHA site key (data-sitekey)
            page_url: The URL of the page with the captcha
            
        Returns:
            The captcha solution token, or None if solving failed
        """
        print(f"Submitting reCAPTCHA to 2Captcha (sitekey: {site_key[:20]}...)")
        
        # Step 1: Submit the captcha
        captcha_id = self._submit_captcha(site_key, page_url)
        if not captcha_id:
            return None
        
        print(f"Captcha submitted, ID: {captcha_id}")
        print("Waiting for solution (this may take 15-60 seconds)...")
        
        # Step 2: Poll for the solution
        solution = self._get_solution(captcha_id)
        
        if solution:
            print("✓ Captcha solved successfully!")
        else:
            print("✗ Failed to solve captcha")
        
        return solution
    
    def _submit_captcha(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Submit a captcha to 2Captcha for solving.
        
        Returns:
            The captcha ID if successful, None otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/in.php",
                data={
                    "key": self.api_key,
                    "method": "userrecaptcha",
                    "googlekey": site_key,
                    "pageurl": page_url,
                    "json": 1
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 1:
                return data.get("request")
            else:
                error = data.get("request", "Unknown error")
                print(f"Error submitting captcha: {error}")
                return None
                
        except Exception as e:
            print(f"Exception submitting captcha: {e}")
            return None
    
    def _get_solution(self, captcha_id: str) -> Optional[str]:
        """
        Poll 2Captcha for the solution to a submitted captcha.
        
        Args:
            captcha_id: The ID returned when submitting the captcha
            
        Returns:
            The solution token if successful, None otherwise
        """
        start_time = time.time()
        wait_time = 5  # Start checking after 5 seconds
        
        while time.time() - start_time < self.timeout:
            time.sleep(wait_time)
            
            try:
                response = requests.get(
                    f"{self.base_url}/res.php",
                    params={
                        "key": self.api_key,
                        "action": "get",
                        "id": captcha_id,
                        "json": 1
                    },
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == 1:
                    # Solution ready
                    return data.get("request")
                elif data.get("request") == "CAPCHA_NOT_READY":
                    # Still processing
                    elapsed = int(time.time() - start_time)
                    print(f"  Still solving... ({elapsed}s elapsed)")
                    wait_time = 5  # Check every 5 seconds
                else:
                    # Error
                    error = data.get("request", "Unknown error")
                    print(f"Error getting solution: {error}")
                    return None
                    
            except Exception as e:
                print(f"Exception getting solution: {e}")
                time.sleep(5)
        
        print(f"Timeout after {self.timeout} seconds")
        return None
    
    def report_bad(self, captcha_id: str) -> bool:
        """
        Report a captcha as incorrectly solved (get refund).
        
        Args:
            captcha_id: The ID of the captcha to report
            
        Returns:
            True if reported successfully
        """
        try:
            response = requests.get(
                f"{self.base_url}/res.php",
                params={
                    "key": self.api_key,
                    "action": "reportbad",
                    "id": captcha_id,
                    "json": 1
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("status") == 1
        except Exception as e:
            print(f"Error reporting bad captcha: {e}")
            return False


def test_api_key():
    """Test the 2Captcha API key and show balance."""
    print("Testing 2Captcha API connection...")
    
    try:
        solver = CaptchaSolver()
        print(f"✓ API key is valid")
        
        balance = solver.get_balance()
        print(f"✓ Account balance: ${balance:.2f}")
        
        if balance < 0.01:
            print("⚠ Warning: Low balance. Add funds at https://2captcha.com")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    # Test the API when run directly
    test_api_key()


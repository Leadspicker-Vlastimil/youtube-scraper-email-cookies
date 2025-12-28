"""Main script for batch processing YouTube channel scraping."""
import argparse
import sys
import time
from typing import List
from scraper import YouTubeScraper
from data_exporter import DataExporter
from session_manager import SessionManager
from captcha_solver import CaptchaSolver
import config


class BatchScraper:
    """Handles batch processing of multiple YouTube channels."""
    
    def __init__(self, output_dir: str = ".", headless: bool = None):
        """
        Initialize batch scraper.
        
        Args:
            output_dir: Directory to save output files
            headless: Whether to run browser in headless mode
        """
        self.output_dir = output_dir
        self.headless = headless if headless is not None else config.HEADLESS
        
        self.session_manager = SessionManager()
        self.captcha_solver = CaptchaSolver()
        self.scraper = YouTubeScraper(
            session_manager=self.session_manager,
            captcha_solver=self.captcha_solver
        )
        self.exporter = DataExporter(output_dir=output_dir)
        
        self.results = []
        self.failed_urls = []
    
    def scrape_channels(self, channel_urls: List[str], output_filename: str = "results"):
        """
        Scrape multiple channels and export results.
        
        Args:
            channel_urls: List of YouTube channel URLs
            output_filename: Base filename for output files (without extension)
        """
        total = len(channel_urls)
        print(f"\n{'='*60}")
        print(f"Starting batch scrape of {total} channel(s)")
        print(f"Output directory: {self.output_dir}")
        print(f"Output filename: {output_filename}")
        print(f"Headless mode: {self.headless}")
        print(f"{'='*60}\n")
        
        # Start the browser
        try:
            print("Starting browser...")
            self.scraper.start(headless=self.headless)
            print("✓ Browser started\n")
        except Exception as e:
            print(f"✗ Failed to start browser: {e}")
            return
        
        # Scrape each channel
        for i, url in enumerate(channel_urls, 1):
            print(f"\n[{i}/{total}] Processing: {url}")
            
            try:
                data = self.scraper.scrape_channel(url)
                
                if data:
                    self.results.append(data)
                    print(f"✓ Successfully scraped channel {i}/{total}")
                    
                    # Save incrementally
                    self.exporter.export_both([data], base_filename=output_filename, append=True)
                else:
                    self.failed_urls.append(url)
                    print(f"✗ Failed to scrape channel {i}/{total}")
                
            except KeyboardInterrupt:
                print("\n\n⚠ Interrupted by user. Saving results...")
                break
            except Exception as e:
                print(f"✗ Error scraping {url}: {e}")
                self.failed_urls.append(url)
            
            # Rate limiting delay between channels
            if i < total:
                delay = config.DELAY_BETWEEN_PROFILES
                print(f"Waiting {delay} seconds before next channel...")
                time.sleep(delay)
        
        # Close browser
        print("\nClosing browser...")
        self.scraper.close()
        
        # Print summary
        self.print_summary(output_filename)
    
    def print_summary(self, output_filename: str):
        """Print scraping summary."""
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total channels processed: {len(self.results) + len(self.failed_urls)}")
        print(f"Successfully scraped: {len(self.results)}")
        print(f"Failed: {len(self.failed_urls)}")
        
        if self.failed_urls:
            print("\nFailed URLs:")
            for url in self.failed_urls:
                print(f"  - {url}")
        
        if self.results:
            print(f"\n✓ Results saved to:")
            print(f"  - {self.output_dir}/{output_filename}.json")
            print(f"  - {self.output_dir}/{output_filename}.csv")
            
            # Print emails found
            emails_found = [r.get('email') for r in self.results if r.get('email')]
            if emails_found:
                print(f"\n✓ Emails found: {len(emails_found)}/{len(self.results)}")
                for email in emails_found:
                    print(f"  - {email}")


def load_urls_from_file(filepath: str) -> List[str]:
    """
    Load channel URLs from a text file (one URL per line).
    
    Args:
        filepath: Path to the file
        
    Returns:
        List of URLs
    """
    urls = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    # Ensure URL is properly formatted
                    if not line.startswith('http'):
                        line = f"https://www.youtube.com/{line}"
                    urls.append(line)
        print(f"✓ Loaded {len(urls)} URL(s) from {filepath}")
        return urls
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description='YouTube Profile Scraper - Extract channel information including hidden emails',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single channel
  python main.py --url "https://www.youtube.com/@NetworkChuck"
  
  # Scrape multiple channels from a file
  python main.py --input channels.txt --output my_results
  
  # Run in headless mode
  python main.py --input channels.txt --headless
  
  # Specify output directory
  python main.py --input channels.txt --output-dir ./results
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', type=str, help='Single YouTube channel URL to scrape')
    input_group.add_argument('--input', type=str, help='Text file with channel URLs (one per line)')
    
    # Output options
    parser.add_argument('--output', type=str, default='results',
                        help='Base filename for output files (default: results)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Directory to save output files (default: current directory)')
    
    # Browser options
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='Run browser with GUI (default)')
    parser.set_defaults(headless=None)
    
    # Other options
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    
    args = parser.parse_args()
    
    # Get channel URLs
    if args.url:
        channel_urls = [args.url]
    else:
        channel_urls = load_urls_from_file(args.input)
    
    if not channel_urls:
        print("✗ No channel URLs to process")
        sys.exit(1)
    
    # Create batch scraper
    batch_scraper = BatchScraper(
        output_dir=args.output_dir,
        headless=args.headless
    )
    
    # Run scraping
    try:
        batch_scraper.scrape_channels(channel_urls, output_filename=args.output)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


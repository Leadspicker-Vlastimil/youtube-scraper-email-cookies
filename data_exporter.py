"""Data export functionality for YouTube scraper results."""
import json
import csv
import os
from typing import List, Dict, Any
from datetime import datetime


class DataExporter:
    """Handles exporting scraped data to JSON and CSV formats."""
    
    def __init__(self, output_dir: str = "."):
        """
        Initialize the exporter.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_json(self, data: List[Dict[str, Any]], filename: str = None, append: bool = True) -> str:
        """
        Export data to JSON file.
        
        Args:
            data: List of channel data dictionaries
            filename: Output filename. If None, generates one with timestamp.
            append: If True and file exists, append to existing data. If False, overwrite.
            
        Returns:
            Path to the output file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_channels_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Handle append mode
        existing_data = []
        if append and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except:
                existing_data = []
        
        # Combine existing and new data
        all_data = existing_data + data
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(data)} channel(s) to JSON: {filepath}")
        print(f"  Total channels in file: {len(all_data)}")
        
        return filepath
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None, append: bool = True) -> str:
        """
        Export data to CSV file.
        
        Args:
            data: List of channel data dictionaries
            filename: Output filename. If None, generates one with timestamp.
            append: If True and file exists, append rows. If False, overwrite.
            
        Returns:
            Path to the output file
        """
        if not data:
            print("⚠ No data to export to CSV")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_channels_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Flatten social_links if present
        flattened_data = []
        for item in data:
            flat_item = item.copy()
            
            # Convert social_links dict to string
            if 'social_links' in flat_item and isinstance(flat_item['social_links'], dict):
                social_links = flat_item['social_links']
                flat_item['social_links'] = '; '.join([f"{k}: {v}" for k, v in social_links.items()])
            
            flattened_data.append(flat_item)
        
        # Determine all possible fields
        all_fields = set()
        for item in flattened_data:
            all_fields.update(item.keys())
        
        # Define field order (common fields first)
        priority_fields = [
            'channel_url', 'channel_handle', 'channel_name', 'email',
            'subscribers', 'video_count', 'total_views', 'joined_date',
            'country', 'description', 'social_links', 'scraped_at'
        ]
        
        # Create ordered field list
        fieldnames = [f for f in priority_fields if f in all_fields]
        remaining_fields = sorted(all_fields - set(fieldnames))
        fieldnames.extend(remaining_fields)
        
        # Determine if we need to write headers
        file_exists = os.path.exists(filepath)
        write_header = not (append and file_exists)
        mode = 'a' if (append and file_exists) else 'w'
        
        # Write to CSV
        with open(filepath, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            
            if write_header:
                writer.writeheader()
            
            writer.writerows(flattened_data)
        
        print(f"✓ Exported {len(data)} channel(s) to CSV: {filepath}")
        
        return filepath
    
    def export_both(self, data: List[Dict[str, Any]], base_filename: str = None, append: bool = True) -> tuple:
        """
        Export data to both JSON and CSV files.
        
        Args:
            data: List of channel data dictionaries
            base_filename: Base filename without extension. Extensions will be added.
            append: If True, append to existing files. If False, overwrite.
            
        Returns:
            Tuple of (json_path, csv_path)
        """
        if base_filename:
            json_file = f"{base_filename}.json"
            csv_file = f"{base_filename}.csv"
        else:
            json_file = None
            csv_file = None
        
        json_path = self.export_to_json(data, json_file, append)
        csv_path = self.export_to_csv(data, csv_file, append)
        
        return json_path, csv_path
    
    def load_from_json(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            List of channel data dictionaries
        """
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
        
        print(f"✓ Loaded {len(data)} channel(s) from: {filepath}")
        return data


def test_exporter():
    """Test the data exporter."""
    print("Testing DataExporter...\n")
    
    # Create sample data
    sample_data = [
        {
            "channel_url": "https://www.youtube.com/@NetworkChuck",
            "channel_handle": "NetworkChuck",
            "channel_name": "NetworkChuck",
            "email": "chuck@networkchuck.com",
            "subscribers": "5.04M subscribers",
            "video_count": "553 videos",
            "total_views": "367,524,086 views",
            "joined_date": "Joined Apr 27, 2014",
            "country": "United States",
            "description": "Welcome to NetworkChuck!",
            "social_links": {
                "Twitter": "https://twitter.com/networkchuck",
                "Instagram": "https://instagram.com/networkchuck"
            },
            "scraped_at": "2024-12-28 10:00:00"
        },
        {
            "channel_url": "https://www.youtube.com/@example",
            "channel_handle": "example",
            "channel_name": "Example Channel",
            "email": None,
            "subscribers": "1M subscribers",
            "video_count": "100 videos",
            "total_views": "50,000,000 views",
            "joined_date": "Joined Jan 1, 2020",
            "country": "Canada",
            "description": "Example description",
            "social_links": {},
            "scraped_at": "2024-12-28 10:05:00"
        }
    ]
    
    exporter = DataExporter(output_dir="test_output")
    
    # Test exporting
    json_path, csv_path = exporter.export_both(sample_data, base_filename="test_channels", append=False)
    
    # Test loading
    loaded_data = exporter.load_from_json("test_channels.json")
    
    print(f"\n✓ Test complete!")
    print(f"  Loaded {len(loaded_data)} channels from JSON")
    
    # Clean up test files
    import shutil
    if os.path.exists("test_output"):
        shutil.rmtree("test_output")
        print("  Cleaned up test files")


if __name__ == "__main__":
    test_exporter()


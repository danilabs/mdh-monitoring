"""
Downloader module for fetching the Million Dollar Homepage.
"""

import requests
from typing import Optional
import os


class WebDownloader:
    """Downloads web content from URLs."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the downloader.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def download_page(self, url: str, output_file: str = "web.html") -> bool:
        """
        Download a web page and save it to a file.
        
        Args:
            url: The URL to download
            output_file: The filename to save the content to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"Downloading {url}...")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"Successfully downloaded to {output_file}")
            return True
            
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return False
        except IOError as e:
            print(f"Error saving file {output_file}: {e}")
            return False
    
    def get_file_size(self, filename: str) -> Optional[int]:
        """
        Get the size of a downloaded file.
        
        Args:
            filename: The file to check
            
        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            return os.path.getsize(filename)
        except OSError:
            return None
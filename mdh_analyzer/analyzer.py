"""
Main analyzer module for the Million Dollar Homepage data extraction.
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from urllib.parse import urlparse
from .downloader import WebDownloader
from .parser import HTMLMapParser


class MillionDollarAnalyzer:
    """Main analyzer class for extracting and processing Million Dollar Homepage data."""
    
    def __init__(self, url: str = "http://www.milliondollarhomepage.com/"):
        """
        Initialize the analyzer.
        
        Args:
            url: URL of the Million Dollar Homepage
        """
        self.url = url
        self.html_file = "web.html"
        self.downloader = WebDownloader()
        self.parser = None
        
    def download_page(self) -> bool:
        """
        Download the Million Dollar Homepage.
        
        Returns:
            True if successful, False otherwise
        """
        return self.downloader.download_page(self.url, self.html_file)
    
    def analyze(self, download_fresh: bool = True) -> Dict[str, Any]:
        """
        Perform complete analysis of the Million Dollar Homepage.
        
        Args:
            download_fresh: Whether to download a fresh copy of the page
            
        Returns:
            Dictionary containing the complete analysis
        """
        # Download page if requested
        if download_fresh:
            if not self.download_page():
                raise Exception("Failed to download the Million Dollar Homepage")
        
        # Initialize parser
        self.parser = HTMLMapParser(self.html_file)
        
        # Validate HTML structure
        if not self.parser.validate_html_structure():
            raise Exception("Invalid HTML structure - map elements not found")
        
        # Extract areas
        areas = self.parser.extract_map_areas()
        
        # Process data
        processed_data = self._process_areas(areas)
        
        # Generate metadata
        metadata = self._generate_metadata(areas)
        
        # Generate summary statistics
        summary_stats = self._generate_summary_statistics(processed_data)
        
        return {
            "metadata": metadata,
            "summary_statistics": summary_stats,
            "domains": processed_data
        }
    
    def _extract_domain_from_url(self, url: str) -> tuple[str, str]:
        """
        Extract domain name from URL and return both domain and cleaned URL.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            Tuple of (domain, cleaned_url). Returns ("", "") for invalid URLs.
        """
        if not url or not url.strip():
            return ("", "")
        
        original_url = url.strip()
        
        try:
            # Handle URLs that don't start with http/https
            if not url.startswith(('http://', 'https://')):
                if url.startswith('//'):
                    url = 'http:' + url
                elif not url.startswith('http'):
                    url = 'http://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check for invalid domains (spaces, special characters that indicate it's not a real URL)
            if not domain or ' ' in domain or domain in ['pending order', 'paid & reserved', 'paid and reserved']:
                return ("", "")
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Validate domain has at least one dot (basic domain validation)
            if '.' not in domain:
                return ("", "")
            
            return (domain, original_url)
            
        except Exception:
            # If URL parsing fails, it's likely not a valid URL
            return ("", "")
    
    def _process_areas(self, areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw area data into domain-grouped format.
        
        Args:
            areas: List of raw area data
            
        Returns:
            List of domains with their areas
        """
        # Group areas by domain extracted from URL
        domain_groups = defaultdict(list)
        
        for area in areas:
            url = area.get('url', '')
            domain_key, cleaned_url = self._extract_domain_from_url(url)
            
            # Update the area with cleaned URL
            area_copy = area.copy()
            area_copy['url'] = cleaned_url
            
            domain_groups[domain_key].append(area_copy)
        
        # Convert to required format
        processed_domains = []
        
        for domain, domain_areas in domain_groups.items():
            total_pixels = sum(area['pixels'] for area in domain_areas)
            
            processed_domains.append({
                "domain": domain,
                "total_pixels": total_pixels,
                "areas": domain_areas
            })
        
        # Sort by total pixels (descending)
        processed_domains.sort(key=lambda x: x['total_pixels'], reverse=True)
        
        return processed_domains
    
    def _generate_metadata(self, areas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate metadata for the analysis.
        
        Args:
            areas: List of area data
            
        Returns:
            Metadata dictionary
        """
        total_pixels = sum(area['pixels'] for area in areas)
        unique_domains = len(set(self._extract_domain_from_url(area.get('url', ''))[0] for area in areas))
        
        return {
            "generated_at": datetime.datetime.now().isoformat(),
            "source_file": self.html_file,
            "description": "Million Dollar Homepage pixel data extraction",
            "total_pixels": total_pixels,
            "total_unique_domains": unique_domains,
            "total_areas": len(areas)
        }
    
    def _generate_summary_statistics(self, domains: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics.
        
        Args:
            domains: List of processed domain data
            
        Returns:
            Summary statistics dictionary
        """
        if not domains:
            return {
                "largest_domain_by_pixels": "None",
                "largest_domain_pixels": 0,
                "average_pixels_per_domain": 0.0,
                "average_pixels_per_area": 0.0
            }
        
        # Find largest domain
        largest_domain = domains[0]  # Already sorted by pixels
        
        # Calculate averages
        total_pixels = sum(domain['total_pixels'] for domain in domains)
        total_areas = sum(len(domain['areas']) for domain in domains)
        
        avg_pixels_per_domain = total_pixels / len(domains) if domains else 0
        avg_pixels_per_area = total_pixels / total_areas if total_areas else 0
        
        return {
            "largest_domain_by_pixels": largest_domain['domain'],
            "largest_domain_pixels": largest_domain['total_pixels'],
            "average_pixels_per_domain": round(avg_pixels_per_domain, 2),
            "average_pixels_per_area": round(avg_pixels_per_area, 2)
        }
    
    def save_json(self, data: Dict[str, Any], filename: Optional[str] = None, output_dir: str = "data") -> str:
        """
        Save analysis data to JSON file.
        
        Args:
            data: Analysis data to save
            filename: Optional custom filename
            output_dir: Directory to save the file (default: "data")
            
        Returns:
            The filename that was used
        """
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pixel_data_{timestamp}.json"
        
        # Ensure filename includes the output directory
        if not filename.startswith(output_dir):
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis saved to {filepath}")
        return filepath
    
    def run_complete_analysis(self) -> str:
        """
        Run the complete analysis pipeline and save results.
        
        Returns:
            The filename of the saved JSON file
        """
        print("Starting Million Dollar Homepage analysis...")
        
        # Perform analysis
        data = self.analyze()
        
        # Save results
        filename = self.save_json(data)
        
        # Print summary
        metadata = data['metadata']
        summary = data['summary_statistics']
        
        print(f"\nAnalysis Complete!")
        print(f"Total pixels: {metadata['total_pixels']:,}")
        print(f"Total domains: {metadata['total_unique_domains']:,}")
        print(f"Total areas: {metadata['total_areas']:,}")
        print(f"Largest domain: {summary['largest_domain_by_pixels']} ({summary['largest_domain_pixels']:,} pixels)")
        print(f"Results saved to: {filename}")
        
        return filename


def main():
    """Main entry point for command-line usage."""
    analyzer = MillionDollarAnalyzer()
    try:
        analyzer.run_complete_analysis()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
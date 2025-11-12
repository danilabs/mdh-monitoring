"""
HTML parser module for extracting map data from the Million Dollar Homepage.
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
from urllib.parse import unquote


class HTMLMapParser:
    """Parses HTML map elements to extract pixel area data."""
    
    def __init__(self, html_file: str):
        """
        Initialize the parser with an HTML file.
        
        Args:
            html_file: Path to the HTML file to parse
        """
        self.html_file = html_file
        self.soup = None
        self._load_html()
    
    def _load_html(self) -> None:
        """Load and parse the HTML file."""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.soup = BeautifulSoup(content, 'html.parser')
        except IOError as e:
            raise IOError(f"Could not read HTML file {self.html_file}: {e}")
        except Exception as e:
            raise Exception(f"Could not parse HTML file {self.html_file}: {e}")
    
    def extract_map_areas(self, map_name: str = "Map") -> List[Dict[str, Any]]:
        """
        Extract area elements from the specified map.
        
        Args:
            map_name: Name of the map element to extract from
            
        Returns:
            List of dictionaries containing area data
        """
        if not self.soup:
            raise Exception("HTML not loaded")
        
        # Find the map element
        map_element = self.soup.find('map', {'name': map_name, 'id': map_name})
        if not map_element:
            raise Exception(f"Map with name '{map_name}' not found")
        
        # Extract all area elements
        areas = map_element.find_all('area')
        extracted_areas = []
        
        for area in areas:
            area_data = self._parse_area_element(area)
            if area_data:
                extracted_areas.append(area_data)
        
        return extracted_areas
    
    def _parse_area_element(self, area) -> Optional[Dict[str, Any]]:
        """
        Parse a single area element.
        
        Args:
            area: BeautifulSoup area element
            
        Returns:
            Dictionary with area data or None if invalid
        """
        try:
            coords = area.get('coords', '')
            href = area.get('href', '')
            title = area.get('title', '')
            
            if not coords:
                return None
            
            # Parse coordinates (assuming rect format: x1,y1,x2,y2)
            coord_parts = [int(x.strip()) for x in coords.split(',')]
            if len(coord_parts) != 4:
                return None
            
            x1, y1, x2, y2 = coord_parts
            width = x2 - x1
            height = y2 - y1
            pixels = width * height
            
            # Clean up URL and title
            url = unquote(href) if href else ""
            clean_title = title.strip() if title else ""
            
            return {
                'coords': coords,
                'pixels': pixels,
                'width': width,
                'height': height,
                'title': clean_title,
                'url': url
            }
            
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse area element: {e}")
            return None
    
    def get_total_areas(self) -> int:
        """Get the total number of areas found."""
        try:
            areas = self.extract_map_areas()
            return len(areas)
        except Exception:
            return 0
    
    def validate_html_structure(self) -> bool:
        """
        Validate that the HTML has the expected structure.
        
        Returns:
            True if structure is valid, False otherwise
        """
        if not self.soup:
            return False
        
        # Check for map element
        map_element = self.soup.find('map', {'name': 'Map', 'id': 'Map'})
        if not map_element:
            return False
        
        # Check for area elements
        areas = map_element.find_all('area')
        return len(areas) > 0
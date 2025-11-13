"""
Tests for the Million Dollar Homepage Analyzer
"""

import json
import os
import tempfile
import unittest
from unittest.mock import mock_open, patch

from mdh_analyzer.analyzer import MillionDollarAnalyzer
from mdh_analyzer.downloader import WebDownloader
from mdh_analyzer.parser import HTMLMapParser


class TestMillionDollarAnalyzer(unittest.TestCase):
    """Test cases for MillionDollarAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MillionDollarAnalyzer()
        self.sample_html = """
        <html>
        <body>
        <map name="Map" id="Map">
            <area coords="0,0,10,10" href="http://example1.com" title="Example 1">
            <area coords="10,10,20,20" href="http://example2.com" title="Example 2">
            <area coords="20,20,30,30" href="http://example1.com" title="Example 1">
        </map>
        </body>
        </html>
        """

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.url, "http://www.milliondollarhomepage.com/")
        self.assertEqual(self.analyzer.html_file, "web.html")
        self.assertIsInstance(self.analyzer.downloader, WebDownloader)

    @patch("mdh_analyzer.analyzer.HTMLMapParser")
    @patch("mdh_analyzer.analyzer.WebDownloader.download_page")
    def test_analyze_with_download(self, mock_download, mock_parser_class):
        """Test analyze method with fresh download."""
        # Mock successful download
        mock_download.return_value = True

        # Mock parser
        mock_parser = mock_parser_class.return_value
        mock_parser.validate_html_structure.return_value = True
        mock_parser.extract_map_areas.return_value = [
            {
                "coords": "0,0,10,10",
                "pixels": 100,
                "width": 10,
                "height": 10,
                "title": "Test Domain",
                "url": "http://test.com",
            }
        ]

        result = self.analyzer.analyze(download_fresh=True)

        # Verify structure
        self.assertIn("metadata", result)
        self.assertIn("summary_statistics", result)
        self.assertIn("domains", result)

        # Verify metadata
        metadata = result["metadata"]
        self.assertEqual(metadata["total_pixels"], 100)
        self.assertEqual(metadata["total_unique_domains"], 1)
        self.assertEqual(metadata["total_areas"], 1)

    def test_process_areas(self):
        """Test area processing logic."""
        areas = [
            {"title": "Domain A", "pixels": 100, "url": "http://domaina.com"},
            {"title": "Domain B", "pixels": 200, "url": "http://domainb.com"},
            {"title": "Domain A", "pixels": 50, "url": "http://domaina.com"},
        ]

        result = self.analyzer._process_areas(areas)

        # Should be sorted by total pixels (descending)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["domain"], "domainb.com")
        self.assertEqual(result[0]["total_pixels"], 200)
        self.assertEqual(result[1]["domain"], "domaina.com")
        self.assertEqual(result[1]["total_pixels"], 150)

    def test_generate_summary_statistics(self):
        """Test summary statistics generation."""
        domains = [
            {"domain": "Domain A", "total_pixels": 200, "areas": [{"pixels": 200}]},
            {"domain": "Domain B", "total_pixels": 100, "areas": [{"pixels": 100}]},
        ]

        result = self.analyzer._generate_summary_statistics(domains)

        self.assertEqual(result["largest_domain_by_pixels"], "Domain A")
        self.assertEqual(result["largest_domain_pixels"], 200)
        self.assertEqual(result["average_pixels_per_domain"], 150.0)
        self.assertEqual(result["average_pixels_per_area"], 150.0)


class TestHTMLMapParser(unittest.TestCase):
    """Test cases for HTMLMapParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_html = """
        <html>
        <body>
        <map name="Map" id="Map">
            <area coords="0,0,10,10" href="http://example1.com" title="Example 1">
            <area coords="10,10,20,20" href="http://example2.com" title="Example 2">
        </map>
        </body>
        </html>
        """

    @patch("builtins.open", new_callable=mock_open)
    def test_parser_initialization(self, mock_file):
        """Test parser initialization."""
        mock_file.return_value.read.return_value = self.sample_html

        parser = HTMLMapParser("test.html")
        self.assertEqual(parser.html_file, "test.html")
        self.assertIsNotNone(parser.soup)

    @patch("builtins.open", new_callable=mock_open)
    def test_extract_map_areas(self, mock_file):
        """Test map area extraction."""
        mock_file.return_value.read.return_value = self.sample_html

        parser = HTMLMapParser("test.html")
        areas = parser.extract_map_areas()

        self.assertEqual(len(areas), 2)

        # Check first area
        area1 = areas[0]
        self.assertEqual(area1["coords"], "0,0,10,10")
        self.assertEqual(area1["pixels"], 100)
        self.assertEqual(area1["width"], 10)
        self.assertEqual(area1["height"], 10)
        self.assertEqual(area1["title"], "Example 1")
        self.assertEqual(area1["url"], "http://example1.com")

    @patch("builtins.open", new_callable=mock_open)
    def test_validate_html_structure(self, mock_file):
        """Test HTML structure validation."""
        mock_file.return_value.read.return_value = self.sample_html

        parser = HTMLMapParser("test.html")
        self.assertTrue(parser.validate_html_structure())

        # Test with invalid HTML
        invalid_html = "<html><body>No map here</body></html>"
        mock_file.return_value.read.return_value = invalid_html
        parser._load_html()
        self.assertFalse(parser.validate_html_structure())


class TestWebDownloader(unittest.TestCase):
    """Test cases for WebDownloader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.downloader = WebDownloader()

    def test_downloader_initialization(self):
        """Test downloader initialization."""
        self.assertEqual(self.downloader.timeout, 30)
        self.assertIsNotNone(self.downloader.session)

    @patch("requests.Session.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_page_success(self, mock_file, mock_get):
        """Test successful page download."""
        # Mock successful response
        mock_response = mock_get.return_value
        mock_response.text = "<html>Test content</html>"
        mock_response.raise_for_status.return_value = None

        result = self.downloader.download_page("http://test.com", "test.html")

        self.assertTrue(result)
        mock_file.assert_called_once_with("test.html", "w", encoding="utf-8")
        mock_file.return_value.write.assert_called_once_with(
            "<html>Test content</html>"
        )


if __name__ == "__main__":
    unittest.main()

"""
Tests for the domain analyzer module.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from mdh_analyzer.domain_analyzer import DomainAnalyzer


class TestDomainAnalyzer:
    """Test cases for DomainAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = DomainAnalyzer()

        # Sample pixel data for testing
        self.sample_pixel_data = {
            "metadata": {
                "generated_at": "2025-11-12T19:57:49.506022",
                "source_file": "web.html",
                "description": "Million Dollar Homepage pixel data extraction",
                "total_pixels": 1000,
                "total_unique_domains": 3,
                "total_areas": 5,
            },
            "summary_statistics": {
                "largest_domain_by_pixels": "example.com",
                "largest_domain_pixels": 500,
                "average_pixels_per_domain": 333.33,
                "average_pixels_per_area": 200.0,
            },
            "domains": [
                {
                    "domain": "example.com",
                    "total_pixels": 500,
                    "areas": [
                        {
                            "coords": "100,100,110,110",
                            "pixels": 100,
                            "width": 10,
                            "height": 10,
                            "title": "Example Site",
                            "url": "http://example.com",
                        }
                    ],
                },
                {
                    "domain": "test.org",
                    "total_pixels": 300,
                    "areas": [
                        {
                            "coords": "200,200,220,210",
                            "pixels": 200,
                            "width": 20,
                            "height": 10,
                            "title": "Test Site",
                            "url": "https://test.org",
                        }
                    ],
                },
                {
                    "domain": "demo.net",
                    "total_pixels": 200,
                    "areas": [
                        {
                            "coords": "300,300,310,320",
                            "pixels": 200,
                            "width": 10,
                            "height": 20,
                            "title": "Demo Site",
                            "url": "http://demo.net",
                        }
                    ],
                },
            ],
        }

    def test_extract_domains_from_json(self):
        """Test domain extraction from JSON data."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.sample_pixel_data, f)
            temp_file = f.name

        try:
            domains = self.analyzer.extract_domains_from_json(temp_file)
            expected_domains = ["demo.net", "example.com", "test.org"]  # sorted list
            assert domains == expected_domains
        finally:
            os.unlink(temp_file)

    def test_extract_domains_from_json_file_not_found(self):
        """Test handling of non-existent JSON file."""
        # The implementation returns empty list instead of raising exception
        domains = self.analyzer.extract_domains_from_json("nonexistent.json")
        assert domains == []

    def test_extract_domains_from_json_invalid_json(self):
        """Test handling of invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            # The implementation returns empty list instead of raising exception
            domains = self.analyzer.extract_domains_from_json(temp_file)
            assert domains == []
        finally:
            os.unlink(temp_file)

    @patch("dns.resolver.resolve")
    def test_check_dns_status_success(self, mock_resolve):
        """Test successful DNS resolution."""
        mock_resolve.return_value = MagicMock()

        status, cname = self.analyzer.check_dns_status("example.com")
        assert status == "NOERROR"
        assert cname is None
        mock_resolve.assert_called_once_with("example.com", "A")

    @patch("dns.resolver.resolve")
    def test_check_dns_status_nxdomain(self, mock_resolve):
        """Test DNS NXDOMAIN response."""
        from dns.resolver import NXDOMAIN

        mock_resolve.side_effect = NXDOMAIN()

        status, cname = self.analyzer.check_dns_status("nonexistent.example")
        assert status == "NXDOMAIN"
        # cname could be None or a string depending on _get_cname_record

    @patch("dns.resolver.resolve")
    def test_check_dns_status_timeout(self, mock_resolve):
        """Test DNS timeout."""
        from dns.resolver import Timeout

        mock_resolve.side_effect = Timeout()

        status, cname = self.analyzer.check_dns_status("timeout.example")
        assert status == "TIMEOUT"
        assert cname is None

    @patch("dns.resolver.resolve")
    def test_check_dns_status_other_exception(self, mock_resolve):
        """Test other DNS exceptions."""
        mock_resolve.side_effect = Exception("DNS error")

        status, cname = self.analyzer.check_dns_status("error.example")
        assert status == "ERROR"
        assert cname is None

    @patch("requests.head")
    def test_check_http_status_success(self, mock_head):
        """Test successful HTTP request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        status = self.analyzer.check_http_status("example.com")
        assert status == 200

    @patch("requests.Session.head")
    def test_check_http_status_404(self, mock_head):
        """Test HTTP 404 response."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response

        status = self.analyzer.check_http_status("example.com")
        assert status == 404

    @patch("requests.Session.head")
    def test_check_http_status_timeout(self, mock_head):
        """Test HTTP timeout."""
        from requests.exceptions import Timeout

        mock_head.side_effect = Timeout()

        status = self.analyzer.check_http_status("timeout.example")
        assert status == 0  # Implementation returns 0 for errors

    @patch("requests.Session.head")
    def test_check_http_status_connection_error(self, mock_head):
        """Test HTTP connection error."""
        from requests.exceptions import ConnectionError

        mock_head.side_effect = ConnectionError()

        status = self.analyzer.check_http_status("unreachable.example")
        assert status == 0  # Implementation returns 0 for errors

    @patch("requests.Session.head")
    def test_check_http_status_ssl_error(self, mock_head):
        """Test HTTP SSL error."""
        from requests.exceptions import SSLError

        mock_head.side_effect = SSLError()

        status = self.analyzer.check_http_status("ssl-error.example")
        assert status == 0  # Implementation returns 0 for SSL errors

    @patch("whois.whois")
    def test_check_whois_status_registered(self, mock_whois):
        """Test WHOIS for registered domain."""
        mock_result = MagicMock()
        mock_result.domain_name = "EXAMPLE.COM"
        mock_result.registrar = "Example Registrar"
        mock_whois.return_value = mock_result

        status = self.analyzer.check_whois_status("example.com")
        assert status == "registered"

    @patch("whois.whois")
    def test_check_whois_status_available(self, mock_whois):
        """Test WHOIS for available domain."""
        mock_result = MagicMock()
        mock_result.status = None
        mock_result.creation_date = None
        mock_whois.return_value = mock_result

        status = self.analyzer.check_whois_status("available.example")
        assert status == "available"

    @patch("whois.whois")
    def test_check_whois_status_error(self, mock_whois):
        """Test WHOIS error handling."""
        mock_whois.side_effect = Exception("WHOIS error")

        status = self.analyzer.check_whois_status("error.example")
        assert status == "unknown"

    @patch.object(DomainAnalyzer, "check_dns_status")
    @patch.object(DomainAnalyzer, "check_http_status")
    @patch.object(DomainAnalyzer, "check_whois_status")
    def test_analyze_domain(self, mock_whois, mock_http, mock_dns):
        """Test complete domain analysis."""
        mock_dns.return_value = ("NOERROR", None)
        mock_http.return_value = 200
        mock_whois.return_value = "registered"

        result = self.analyzer.analyze_domain("example.com")

        # Check that all expected keys are present
        assert result["domain"] == "example.com"
        assert result["dns_status"] == "NOERROR"
        assert result["http_status"] == 200
        assert result["whois_status"] == "registered"
        assert "analyzed_at" in result

        mock_dns.assert_called_once_with("example.com")
        mock_http.assert_called_once_with("example.com")
        mock_whois.assert_called_once_with("example.com")

    def test_save_domain_report(self):
        """Test saving domain analysis report."""
        sample_results = [
            {
                "domain": "example.com",
                "dns_status": "NOERROR",
                "http_status": 200,
                "whois_status": "registered",
            },
            {
                "domain": "test.org",
                "dns_status": "NXDOMAIN",
                "http_status": 0,
                "whois_status": "available",
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_report.json")
            self.analyzer.save_domain_report(sample_results, output_path)

            # Check that file was created
            assert os.path.exists(output_path)

            # Check file content
            with open(output_path, "r") as f:
                data = json.load(f)

            # Verify structure
            assert "metadata" in data
            assert "summary" in data
            assert "domains" in data

            # Verify metadata
            metadata = data["metadata"]
            assert metadata["total_domains"] == 2

            # Verify domains data
            assert data["domains"] == sample_results

    def test_save_domain_report_custom_filename(self):
        """Test saving domain report with custom filename."""
        sample_results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_filename = os.path.join(temp_dir, "custom_report.json")
            self.analyzer.save_domain_report(sample_results, custom_filename)

            assert os.path.exists(custom_filename)

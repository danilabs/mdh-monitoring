"""
Markdown Report Generator

This module generates comprehensive markdown reports combining pixel data
and domain analysis results to provide insights into domain status,
availability, and pixel allocations.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkdownReportGenerator:
    """Generates markdown reports from pixel and domain analysis data"""
    
    def __init__(self):
        """Initialize the report generator"""
        self.logger = logger
    
    def load_pixel_data(self, pixel_data_file: str) -> Dict[str, Any]:
        """
        Load pixel data from JSON file
        
        Args:
            pixel_data_file: Path to pixel data JSON file
            
        Returns:
            Dictionary containing pixel data
        """
        try:
            with open(pixel_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading pixel data: {e}")
            return {}
    
    def load_domain_analysis(self, domain_analysis_file: str) -> Dict[str, Any]:
        """
        Load domain analysis data from JSON file
        
        Args:
            domain_analysis_file: Path to domain analysis JSON file
            
        Returns:
            Dictionary containing domain analysis data
        """
        try:
            with open(domain_analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading domain analysis: {e}")
            return {}
    
    def create_domain_pixel_map(self, pixel_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Create a mapping of domains to their total pixel counts
        
        Args:
            pixel_data: Pixel data dictionary
            
        Returns:
            Dictionary mapping domain names to pixel counts
        """
        domain_pixels = {}
        
        for domain_entry in pixel_data.get('domains', []):
            domain = domain_entry.get('domain', '').strip()
            pixels = domain_entry.get('total_pixels', 0)
            if domain and domain != '':
                domain_pixels[domain] = pixels
        
        return domain_pixels
    
    def generate_report(self, pixel_data_file: str, domain_analysis_file: str, 
                       output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive markdown report
        
        Args:
            pixel_data_file: Path to pixel data JSON file
            domain_analysis_file: Path to domain analysis JSON file
            output_file: Optional output file path
            
        Returns:
            Path to generated markdown report
        """
        # Load data
        pixel_data = self.load_pixel_data(pixel_data_file)
        domain_analysis = self.load_domain_analysis(domain_analysis_file)
        
        if not pixel_data or not domain_analysis:
            raise ValueError("Failed to load required data files")
        
        # Create domain-pixel mapping
        domain_pixels = self.create_domain_pixel_map(pixel_data)
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"reports/report_{timestamp}.md"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Generate report content
        report_content = self._generate_report_content(
            pixel_data, domain_analysis, domain_pixels
        )
        
        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Markdown report generated: {output_file}")
        return output_file
    
    def _generate_report_content(self, pixel_data: Dict[str, Any], 
                                domain_analysis: Dict[str, Any],
                                domain_pixels: Dict[str, int]) -> str:
        """
        Generate the actual markdown report content
        
        Args:
            pixel_data: Pixel data dictionary
            domain_analysis: Domain analysis dictionary
            domain_pixels: Domain to pixel count mapping
            
        Returns:
            Markdown report content as string
        """
        # Extract metadata
        pixel_meta = pixel_data.get('metadata', {})
        domain_meta = domain_analysis.get('metadata', {})
        domain_summary = domain_analysis.get('summary', {})
        
        # Analyze domains by status
        domains_by_status = self._analyze_domains_by_status(
            domain_analysis.get('domains', []), domain_pixels
        )
        
        # Generate report sections
        report_lines = []
        
        # Header
        report_lines.extend(self._generate_header(pixel_meta, domain_meta))
        
        # Executive Summary
        report_lines.extend(self._generate_executive_summary(
            pixel_data, domain_analysis, domains_by_status
        ))
        
        # Domain Status Analysis
        report_lines.extend(self._generate_domain_status_analysis(domain_summary))
        
        # Available Domains (sorted by pixels)
        report_lines.extend(self._generate_available_domains_section(
            domains_by_status.get('available', [])
        ))
        
        # NXDOMAIN Analysis
        report_lines.extend(self._generate_nxdomain_section(
            domains_by_status.get('nxdomain', [])
        ))
        
        # Top Domains by Pixels
        report_lines.extend(self._generate_top_domains_section(
            domains_by_status.get('registered', [])
        ))
        
        # Technical Details
        report_lines.extend(self._generate_technical_details(
            pixel_meta, domain_meta
        ))
        
        return '\n'.join(report_lines)
    
    def _analyze_domains_by_status(self, domains: List[Dict], 
                                  domain_pixels: Dict[str, int]) -> Dict[str, List[Dict]]:
        """
        Analyze and categorize domains by their status
        
        Args:
            domains: List of domain analysis results
            domain_pixels: Domain to pixel count mapping
            
        Returns:
            Dictionary categorizing domains by status
        """
        categorized = {
            'available': [],
            'registered': [],
            'nxdomain': [],
            'unknown': []
        }
        
        for domain_info in domains:
            domain = domain_info.get('domain', '')
            dns_status = domain_info.get('dns_status', '')
            whois_status = domain_info.get('whois_status', '')
            http_status = domain_info.get('http_status', 0)
            
            # Add pixel count information
            domain_info_with_pixels = domain_info.copy()
            domain_info_with_pixels['pixels'] = domain_pixels.get(domain, 0)
            
            # Categorize based on status
            if whois_status == 'available':
                categorized['available'].append(domain_info_with_pixels)
            elif dns_status == 'NXDOMAIN':
                categorized['nxdomain'].append(domain_info_with_pixels)
            elif whois_status == 'registered' or http_status > 0:
                categorized['registered'].append(domain_info_with_pixels)
            else:
                categorized['unknown'].append(domain_info_with_pixels)
        
        # Sort each category by pixel count (descending)
        for category in categorized:
            categorized[category].sort(key=lambda x: x.get('pixels', 0), reverse=True)
        
        return categorized
    
    def _generate_header(self, pixel_meta: Dict, domain_meta: Dict) -> List[str]:
        """Generate report header"""
        analysis_date = domain_meta.get('generated_at', 'Unknown')
        if analysis_date != 'Unknown':
            try:
                dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                analysis_date = dt.strftime('%B %d, %Y at %H:%M UTC')
            except:
                pass
        
        return [
            "# Million Dollar Homepage - Domain Analysis Report",
            "",
            f"**Analysis Date:** {analysis_date}",
            f"**Source Data:** {pixel_meta.get('source_file', 'web.html')}",
            "",
            "---",
            ""
        ]
    
    def _generate_executive_summary(self, pixel_data: Dict, domain_analysis: Dict,
                                   domains_by_status: Dict) -> List[str]:
        """Generate executive summary section"""
        pixel_meta = pixel_data.get('metadata', {})
        domain_meta = domain_analysis.get('metadata', {})
        
        total_domains = domain_meta.get('total_domains', 0)
        total_pixels = pixel_meta.get('total_pixels', 0)
        total_areas = pixel_meta.get('total_areas', 0)
        
        available_count = len(domains_by_status.get('available', []))
        nxdomain_count = len(domains_by_status.get('nxdomain', []))
        registered_count = len(domains_by_status.get('registered', []))
        
        # Calculate total pixels for available domains
        available_pixels = sum(d.get('pixels', 0) for d in domains_by_status.get('available', []))
        
        return [
            "## 📊 Executive Summary",
            "",
            f"This report analyzes **{total_domains:,} unique domains** found across **{total_pixels:,} pixels** in **{total_areas:,} areas** of the Million Dollar Homepage.",
            "",
            "### Key Findings:",
            "",
            f"- 🟢 **{registered_count:,} domains ({registered_count/total_domains*100:.1f}%)** are registered and potentially active",
            f"- 🔴 **{nxdomain_count:,} domains ({nxdomain_count/total_domains*100:.1f}%)** no longer exist (NXDOMAIN)",
            f"- 🟡 **{available_count:,} domains ({available_count/total_domains*100:.1f}%)** are available for purchase",
            f"- 💰 **{available_pixels:,} pixels** are associated with available domains",
            "",
            "---",
            ""
        ]
    
    def _generate_domain_status_analysis(self, domain_summary: Dict) -> List[str]:
        """Generate domain status analysis section"""
        dns_dist = domain_summary.get('dns_status_distribution', {})
        http_dist = domain_summary.get('http_status_distribution', {})
        whois_dist = domain_summary.get('whois_status_distribution', {})
        
        return [
            "## 🔍 Domain Status Analysis",
            "",
            "### DNS Resolution Status",
            "",
            "| Status | Count | Description |",
            "|--------|-------|-------------|",
            f"| NOERROR | {dns_dist.get('NOERROR', 0):,} | Domain resolves successfully |",
            f"| NXDOMAIN | {dns_dist.get('NXDOMAIN', 0):,} | Domain does not exist |",
            f"| TIMEOUT | {dns_dist.get('TIMEOUT', 0):,} | DNS query timed out |",
            f"| ERROR | {dns_dist.get('ERROR', 0):,} | Other DNS resolution error |",
            "",
            "### HTTP Availability",
            "",
            "| Status | Count | Description |",
            "|--------|-------|-------------|",
            f"| Success (2xx) | {http_dist.get('success', 0):,} | Website is accessible |",
            f"| Redirect (3xx) | {http_dist.get('redirect', 0):,} | Website redirects |",
            f"| Client Error (4xx) | {http_dist.get('client_error', 0):,} | Page not found, etc. |",
            f"| Server Error (5xx) | {http_dist.get('server_error', 0):,} | Server issues |",
            f"| Unreachable | {http_dist.get('unreachable', 0):,} | Cannot connect |",
            "",
            "### WHOIS Registration Status",
            "",
            "| Status | Count | Description |",
            "|--------|-------|-------------|",
            f"| Registered | {whois_dist.get('registered', 0):,} | Domain is registered |",
            f"| Available | {whois_dist.get('available', 0):,} | Domain is available for purchase |",
            f"| Unknown | {whois_dist.get('unknown', 0):,} | Could not determine status |",
            "",
            "---",
            ""
        ]
    
    def _generate_available_domains_section(self, available_domains: List[Dict]) -> List[str]:
        """Generate available domains section"""
        if not available_domains:
            return [
                "## 🛒 Available Domains for Purchase",
                "",
                "No domains are currently available for purchase.",
                "",
                "---",
                ""
            ]
        
        total_pixels = sum(d.get('pixels', 0) for d in available_domains)
        
        lines = [
            "## 🛒 Available Domains for Purchase",
            "",
            f"**{len(available_domains):,} domains** are available for purchase, representing **{total_pixels:,} pixels** of the Million Dollar Homepage.",
            "",
            "### All Available Domains by Pixel Count",
            "",
            "| Domain | Pixels | DNS Status | HTTP Status |",
            "|--------|--------|------------|-------------|"
        ]
        
        # Show ALL available domains (not just top 20)
        for domain_info in available_domains:
            domain = domain_info.get('domain', '')
            pixels = domain_info.get('pixels', 0)
            dns_status = domain_info.get('dns_status', '')
            http_status = domain_info.get('http_status', 0)
            
            lines.append(f"| `{domain}` | {pixels:,} | {dns_status} | {http_status} |")
        
        lines.extend([
            "",
            "---",
            ""
        ])
        
        return lines
    
    def _generate_nxdomain_section(self, nxdomain_domains: List[Dict]) -> List[str]:
        """Generate NXDOMAIN analysis section"""
        if not nxdomain_domains:
            return []
        
        total_pixels = sum(d.get('pixels', 0) for d in nxdomain_domains)
        
        lines = [
            "## ❌ Non-Existent Domains (NXDOMAIN)",
            "",
            f"**{len(nxdomain_domains):,} domains** no longer exist, representing **{total_pixels:,} pixels** of lost content.",
            "",
            "### Top Non-Existent Domains by Pixel Count",
            "",
            "| Domain | Pixels | WHOIS Status | CNAME |",
            "|--------|--------|--------------|-------|"
        ]
        
        # Show top 15 NXDOMAIN domains
        for domain_info in nxdomain_domains[:15]:
            domain = domain_info.get('domain', '')
            pixels = domain_info.get('pixels', 0)
            whois_status = domain_info.get('whois_status', '')
            cname_record = domain_info.get('cname_record', '')
            
            # Only show CNAME if domain is not available for purchase
            cname_display = cname_record if whois_status != 'available' and cname_record else '-'
            
            lines.append(f"| `{domain}` | {pixels:,} | {whois_status} | {cname_display} |")
        
        if len(nxdomain_domains) > 15:
            lines.append(f"| ... | ... | ... | ... |")
            lines.append(f"| *{len(nxdomain_domains) - 15:,} more domains* | | | |")
        
        lines.extend([
            "",
            "---",
            ""
        ])
        
        return lines
    
    def _generate_top_domains_section(self, registered_domains: List[Dict]) -> List[str]:
        """Generate top registered domains section"""
        if not registered_domains:
            return []
        
        lines = [
            "## 🏆 Top Active Domains by Pixel Count",
            "",
            f"These are the largest registered domains still active on the Million Dollar Homepage:",
            "",
            "| Domain | Pixels | DNS Status | HTTP Status | WHOIS Status |",
            "|--------|--------|------------|-------------|--------------|"
        ]
        
        # Show top 15 registered domains
        for domain_info in registered_domains[:15]:
            domain = domain_info.get('domain', '')
            pixels = domain_info.get('pixels', 0)
            dns_status = domain_info.get('dns_status', '')
            http_status = domain_info.get('http_status', 0)
            whois_status = domain_info.get('whois_status', '')
            
            lines.append(f"| `{domain}` | {pixels:,} | {dns_status} | {http_status} | {whois_status} |")
        
        lines.extend([
            "",
            "---",
            ""
        ])
        
        return lines
    
    def _generate_technical_details(self, pixel_meta: Dict, domain_meta: Dict) -> List[str]:
        """Generate technical details section"""
        return [
            "## 🔧 Technical Details",
            "",
            "### Data Sources",
            "",
            f"- **Pixel Data Generated:** {pixel_meta.get('generated_at', 'Unknown')}",
            f"- **Domain Analysis Generated:** {domain_meta.get('generated_at', 'Unknown')}",
            f"- **Source File:** {pixel_meta.get('source_file', 'web.html')}",
            f"- **Total Pixels Analyzed:** {pixel_meta.get('total_pixels', 0):,}",
            f"- **Total Areas Analyzed:** {pixel_meta.get('total_areas', 0):,}",
            f"- **Total Domains Analyzed:** {domain_meta.get('total_domains', 0):,}",
            "",
            "### Analysis Methods",
            "",
            "- **DNS Resolution:** A record lookup with timeout handling",
            "- **HTTP Status:** HEAD requests to both HTTP and HTTPS endpoints",
            "- **WHOIS Lookup:** Registration status verification",
            "- **Pixel Counting:** Extracted from Million Dollar Homepage map coordinates",
            "",
            "---",
            "",
            "*Report generated by Million Dollar Homepage Analyzer*"
        ]


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate markdown reports from pixel and domain data')
    parser.add_argument('pixel_data', help='Path to pixel data JSON file')
    parser.add_argument('domain_analysis', help='Path to domain analysis JSON file')
    parser.add_argument('-o', '--output', help='Output markdown file path')
    
    args = parser.parse_args()
    
    generator = MarkdownReportGenerator()
    output_file = generator.generate_report(
        args.pixel_data, 
        args.domain_analysis, 
        args.output
    )
    
    print(f"Markdown report generated: {output_file}")


if __name__ == '__main__':
    main()
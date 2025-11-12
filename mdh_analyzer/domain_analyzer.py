"""
Domain Analyzer Module

This module analyzes domains extracted from pixel data to determine:
- DNS resolution status (NXDOMAIN, NOERROR, etc.)
- HTTP status code using HEAD requests
- Domain availability status based on WHOIS information
"""

import json
import socket
import requests
import whois
import dns.resolver
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DomainAnalyzer:
    """Analyzes domains for DNS, HTTP, and WHOIS status"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the domain analyzer
        
        Args:
            timeout: Timeout in seconds for HTTP requests
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_domains_from_json(self, json_file_path: str) -> List[str]:
        """
        Extract unique domains from pixel data JSON file
        
        Args:
            json_file_path: Path to the pixel data JSON file
            
        Returns:
            List of unique domain names
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            domains = set()
            
            # Extract domains from the domains array
            for domain_entry in data.get('domains', []):
                domain = domain_entry.get('domain', '').strip()
                if domain and domain != '':
                    domains.add(domain)
            
            return sorted(list(domains))
            
        except Exception as e:
            logger.error(f"Error extracting domains from JSON: {e}")
            return []
    
    def check_dns_status(self, domain: str) -> str:
        """
        Check DNS resolution status for a domain
        
        Args:
            domain: Domain name to check
            
        Returns:
            DNS status code (NOERROR, NXDOMAIN, SERVFAIL, etc.)
        """
        try:
            # Try to resolve A record
            dns.resolver.resolve(domain, 'A')
            return 'NOERROR'
        except dns.resolver.NXDOMAIN:
            return 'NXDOMAIN'
        except dns.resolver.NoAnswer:
            return 'NOERROR'  # Domain exists but no A record
        except dns.resolver.Timeout:
            return 'TIMEOUT'
        except dns.resolver.NoNameservers:
            return 'SERVFAIL'
        except Exception as e:
            logger.debug(f"DNS error for {domain}: {e}")
            return 'ERROR'
    
    def check_http_status(self, domain: str) -> int:
        """
        Check HTTP status using HEAD request
        
        Args:
            domain: Domain name to check
            
        Returns:
            HTTP status code (200, 404, 403, etc.) or 0 if unreachable
        """
        if not domain:
            return 0
            
        # Try both HTTP and HTTPS
        for protocol in ['https', 'http']:
            try:
                url = f"{protocol}://{domain}"
                response = self.session.head(
                    url, 
                    timeout=self.timeout, 
                    allow_redirects=True
                )
                return response.status_code
            except requests.exceptions.SSLError:
                # SSL error, try HTTP if we were trying HTTPS
                if protocol == 'https':
                    continue
                return 0
            except requests.exceptions.RequestException:
                # Connection error, try next protocol
                if protocol == 'https':
                    continue
                return 0
            except Exception as e:
                logger.debug(f"HTTP error for {domain}: {e}")
                if protocol == 'https':
                    continue
                return 0
        
        return 0
    
    def check_whois_status(self, domain: str) -> str:
        """
        Check domain availability status using WHOIS
        
        Args:
            domain: Domain name to check
            
        Returns:
            Status: 'registered', 'available', or 'unknown'
        """
        if not domain:
            return 'unknown'
            
        try:
            w = whois.whois(domain)
            
            # Check if domain is registered
            if w.status is not None or w.creation_date is not None:
                return 'registered'
            elif w.status is None and w.creation_date is None:
                return 'available'
            else:
                return 'registered'
                
        except whois.exceptions.WhoisDomainNotFoundError:
            # Domain might be available or unsupported TLD
            return 'available'
        except Exception as e:
            logger.debug(f"WHOIS error for {domain}: {e}")
            return 'unknown'
    
    def analyze_domain(self, domain: str) -> Dict:
        """
        Perform complete analysis of a single domain
        
        Args:
            domain: Domain name to analyze
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing domain: {domain}")
        
        result = {
            'domain': domain,
            'dns_status': self.check_dns_status(domain),
            'http_status': self.check_http_status(domain),
            'whois_status': self.check_whois_status(domain),
            'analyzed_at': datetime.now(timezone.utc).isoformat()
        }
        
        return result
    
    def analyze_domains_from_json(self, json_file_path: str) -> List[Dict]:
        """
        Analyze all domains from a pixel data JSON file
        
        Args:
            json_file_path: Path to the pixel data JSON file
            
        Returns:
            List of domain analysis results
        """
        domains = self.extract_domains_from_json(json_file_path)
        results = []
        
        logger.info(f"Found {len(domains)} unique domains to analyze")
        
        for i, domain in enumerate(domains, 1):
            logger.info(f"Processing domain {i}/{len(domains)}: {domain}")
            result = self.analyze_domain(domain)
            results.append(result)
        
        return results
    
    def save_domain_report(self, results: List[Dict], output_path: str) -> None:
        """
        Save domain analysis results to JSON file
        
        Args:
            results: List of domain analysis results
            output_path: Path to save the report
        """
        report = {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'total_domains': len(results),
                'description': 'Domain analysis report from Million Dollar Homepage pixel data'
            },
            'summary': self._generate_summary(results),
            'domains': results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Domain report saved to: {output_path}")
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from analysis results"""
        if not results:
            return {}
        
        dns_stats = {}
        http_stats = {}
        whois_stats = {}
        
        for result in results:
            # DNS statistics
            dns_status = result['dns_status']
            dns_stats[dns_status] = dns_stats.get(dns_status, 0) + 1
            
            # HTTP statistics
            http_status = result['http_status']
            if http_status == 0:
                http_key = 'unreachable'
            elif 200 <= http_status < 300:
                http_key = 'success'
            elif 300 <= http_status < 400:
                http_key = 'redirect'
            elif 400 <= http_status < 500:
                http_key = 'client_error'
            elif 500 <= http_status < 600:
                http_key = 'server_error'
            else:
                http_key = 'other'
            
            http_stats[http_key] = http_stats.get(http_key, 0) + 1
            
            # WHOIS statistics
            whois_status = result['whois_status']
            whois_stats[whois_status] = whois_stats.get(whois_status, 0) + 1
        
        return {
            'dns_status_distribution': dns_stats,
            'http_status_distribution': http_stats,
            'whois_status_distribution': whois_stats
        }


def main():
    """Main function for command-line usage"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Analyze domains from pixel data')
    parser.add_argument('input_file', help='Path to pixel data JSON file')
    parser.add_argument('-o', '--output', help='Output directory for reports', default='reports')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='HTTP timeout in seconds')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize analyzer
    analyzer = DomainAnalyzer(timeout=args.timeout)
    
    # Analyze domains
    results = analyzer.analyze_domains_from_json(args.input_file)
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(args.output, f'report_{timestamp}.json')
    
    # Save report
    analyzer.save_domain_report(results, output_file)
    
    print(f"Analysis complete! Report saved to: {output_file}")
    print(f"Analyzed {len(results)} domains")


if __name__ == '__main__':
    main()
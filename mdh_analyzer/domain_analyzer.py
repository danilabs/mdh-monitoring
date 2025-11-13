"""
Domain Analyzer Module

This module analyzes domains extracted from pixel data to determine:
- DNS resolution status (NXDOMAIN, NOERROR, etc.)
- HTTP status code using HEAD requests
- Domain availability status based on WHOIS information
"""
# pylint: disable=no-name-in-module

import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import dns.resolver
import requests
import whois

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DomainAnalyzer:
    """Analyzes domains for DNS, HTTP, and WHOIS status"""

    def __init__(self, timeout: int = 10, max_workers: int = 10):
        """
        Initialize the domain analyzer

        Args:
            timeout: Timeout in seconds for HTTP requests
            max_workers: Maximum number of concurrent threads for analysis
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self._lock = threading.Lock()

    def extract_domains_from_json(self, json_file_path: str) -> List[str]:
        """
        Extract unique domains from pixel data JSON file

        Args:
            json_file_path: Path to the pixel data JSON file

        Returns:
            List of unique domain names
        """
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            domains = set()

            # Extract domains from the domains array
            for domain_entry in data.get("domains", []):
                domain = domain_entry.get("domain", "").strip()
                if domain and domain != "":
                    domains.add(domain)

            return sorted(list(domains))

        except (IOError, json.JSONDecodeError, KeyError) as e:
            logger.error("Error extracting domains from JSON: %s", e)
            return []

    def check_dns_status(self, domain: str) -> Tuple[str, Optional[str]]:
        """
        Check DNS resolution status for a domain

        Args:
            domain: Domain name to check

        Returns:
            Tuple of (DNS status code, CNAME record if available)
        """
        try:
            # Try to resolve A record
            dns.resolver.resolve(domain, "A")
            return ("NOERROR", None)
        except dns.resolver.NXDOMAIN:
            # Check for CNAME record even if NXDOMAIN
            cname = self._get_cname_record(domain)
            return ("NXDOMAIN", cname)
        except dns.resolver.NoAnswer:
            return ("NOERROR", None)  # Domain exists but no A record
        except dns.resolver.Timeout:
            return ("TIMEOUT", None)
        except dns.resolver.NoNameservers:
            return ("SERVFAIL", None)
        except (dns.exception.DNSException, OSError, Exception) as e:
            logger.debug("DNS error for %s: %s", domain, str(e))
            return ("ERROR", None)

    def _get_cname_record(self, domain: str) -> Optional[str]:
        """
        Get CNAME record for a domain

        Args:
            domain: Domain name to check

        Returns:
            CNAME record if available, None otherwise
        """
        try:
            answers = dns.resolver.resolve(domain, "CNAME")
            if answers:
                return str(answers[0]).rstrip(".")
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.Timeout,
            dns.resolver.NoNameservers,
            dns.exception.DNSException,
        ):
            pass
        return None

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
        for protocol in ["https", "http"]:
            try:
                url = f"{protocol}://{domain}"
                response = self.session.head(
                    url, timeout=self.timeout, allow_redirects=True
                )
                return response.status_code
            except requests.exceptions.SSLError:
                # SSL error, try HTTP if we were trying HTTPS
                if protocol == "https":
                    continue
                return 0
            except requests.exceptions.RequestException as e:
                logger.debug("HTTP error for %s: %s", domain, e)
                # Connection error, try next protocol
                if protocol == "https":
                    continue
                return 0
            except (OSError, ValueError) as e:
                logger.debug("HTTP error for %s: %s", domain, e)
                if protocol == "https":
                    continue
                return 0

        return 0

    def check_whois_status(self, domain: str) -> Tuple[str, Dict]:
        """
        Check domain availability status using WHOIS and extract detailed information

        Args:
            domain: Domain name to check

        Returns:
            Tuple of (Status: 'registered', 'available', or 'unknown', WHOIS details dict)
        """
        if not domain:
            return "unknown", {}

        try:
            w = whois.whois(domain)
            whois_details = {}

            # Extract detailed WHOIS information
            if w.creation_date:
                # Handle both single dates and lists of dates
                creation_date = w.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0] if creation_date else None
                if creation_date:
                    whois_details["registered_at"] = creation_date.isoformat() if hasattr(creation_date, 'isoformat') else str(creation_date)

            if w.expiration_date:
                # Handle both single dates and lists of dates
                expiry_date = w.expiration_date
                if isinstance(expiry_date, list):
                    expiry_date = expiry_date[0] if expiry_date else None
                if expiry_date:
                    whois_details["expiry_date"] = expiry_date.isoformat() if hasattr(expiry_date, 'isoformat') else str(expiry_date)

            if w.updated_date:
                # Handle both single dates and lists of dates
                updated_date = w.updated_date
                if isinstance(updated_date, list):
                    updated_date = updated_date[0] if updated_date else None
                if updated_date:
                    whois_details["last_updated"] = updated_date.isoformat() if hasattr(updated_date, 'isoformat') else str(updated_date)

            if w.name_servers:
                # Handle nameservers (can be list or single value)
                nameservers = w.name_servers
                if isinstance(nameservers, list):
                    whois_details["nameservers"] = [ns.lower() if isinstance(ns, str) else str(ns) for ns in nameservers if ns]
                elif nameservers:
                    whois_details["nameservers"] = [str(nameservers).lower()]

            # Check if domain is registered
            if w.status is not None or w.creation_date is not None:
                return "registered", whois_details
            if w.status is None and w.creation_date is None:
                return "available", whois_details
            return "registered", whois_details

        except whois.exceptions.WhoisDomainNotFoundError:
            # Domain might be available or unsupported TLD
            return "available", {}
        except (OSError, ValueError, TypeError, Exception) as e:
            logger.debug("WHOIS error for %s: %s", domain, e)
            return "unknown", {}

    def analyze_domain(self, domain: str, show_progress: bool = True) -> Dict:
        """
        Perform complete analysis of a single domain

        Args:
            domain: Domain name to analyze
            show_progress: Whether to show individual domain progress (for non-threaded mode)

        Returns:
            Dictionary with analysis results
        """
        if show_progress:
            logger.debug("Analyzing domain: %s", domain)

        dns_status, cname_record = self.check_dns_status(domain)
        http_status = self.check_http_status(domain)
        whois_status, whois_details = self.check_whois_status(domain)

        # Determine final availability status based on improved logic
        final_whois_status = self._determine_availability_status(dns_status, whois_status)

        result = {
            "domain": domain,
            "dns_status": dns_status,
            "http_status": http_status,
            "whois_status": final_whois_status,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Add CNAME record if available
        if cname_record:
            result["cname_record"] = cname_record

        # Add detailed WHOIS information if available
        if whois_details:
            result.update(whois_details)

        return result

    def _determine_availability_status(self, dns_status: str, whois_status: str) -> str:
        """
        Determine final availability status based on DNS and WHOIS results

        Args:
            dns_status: DNS resolution status
            whois_status: WHOIS lookup status

        Returns:
            Final availability status: 'registered', 'available', or 'unknown'
        """
        # If DNS returns NOERROR, domain is definitely registered (has DNS configured)
        if dns_status == "NOERROR":
            return "registered"
        
        # If DNS returns NXDOMAIN, check WHOIS to determine if domain is actually registered
        # (some registered domains might not have DNS configured)
        if dns_status == "NXDOMAIN":
            if whois_status == "registered":
                return "registered"  # Domain is registered but DNS not configured
            elif whois_status == "available":
                return "available"   # Domain is truly available
            else:
                return "unknown"     # Cannot determine from WHOIS
        
        # For other DNS statuses (TIMEOUT, SERVFAIL, ERROR), rely on WHOIS
        return whois_status

    def analyze_domains_from_json(
        self, json_file_path: str, use_threading: bool = True
    ) -> List[Dict]:
        """
        Analyze all domains from a pixel data JSON file

        Args:
            json_file_path: Path to the pixel data JSON file
            use_threading: Whether to use threading for concurrent analysis

        Returns:
            List of domain analysis results
        """
        domains = self.extract_domains_from_json(json_file_path)

        logger.info("Found %d unique domains to analyze", len(domains))

        if use_threading:
            return self._analyze_domains_threaded(domains)
        return self._analyze_domains_sequential(domains)

    def _analyze_domains_sequential(self, domains: List[str]) -> List[Dict]:
        """Analyze domains sequentially with progress tracking"""
        results = []
        total_domains = len(domains)

        for i, domain in enumerate(domains, 1):
            result = self.analyze_domain(domain, show_progress=False)
            results.append(result)

            # Show progress every 10%
            progress_percent = (i * 100) // total_domains
            if i == 1 or progress_percent % 10 == 0 or i == total_domains:
                logger.info(
                    "Progress: %s%% (%s/%s domains analyzed)",
                    progress_percent,
                    i,
                    total_domains,
                )

        return results

    def _analyze_domains_threaded(self, domains: List[str]) -> List[Dict]:
        """Analyze domains using threading with progress tracking"""
        results = []
        total_domains = len(domains)
        completed_count = 0
        last_reported_percent = -1

        logger.info("Starting threaded analysis with %d workers", self.max_workers)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_domain = {
                executor.submit(self.analyze_domain, domain, False): domain
                for domain in domains
            }

            # Process completed tasks
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    results.append(result)
                except (requests.exceptions.RequestException, dns.exception.DNSException,
                       OSError, ValueError, TypeError) as e:
                    logger.error("Error analyzing domain %s: %s", domain, e)
                    # Add error result
                    results.append(
                        {
                            "domain": domain,
                            "dns_status": "ERROR",
                            "http_status": 0,
                            "whois_status": "unknown",
                            "analyzed_at": datetime.now(timezone.utc).isoformat(),
                            "error": str(e),
                        }
                    )

                completed_count += 1
                progress_percent = (completed_count * 100) // total_domains

                # Show progress every 10% or at completion
                if progress_percent > last_reported_percent and (
                    progress_percent % 10 == 0 or completed_count == total_domains
                ):
                    logger.info(
                        "Progress: %s%% (%s/%s domains analyzed)",
                        progress_percent,
                        completed_count,
                        total_domains,
                    )
                    last_reported_percent = progress_percent

        # Sort results by domain name to maintain consistency
        results.sort(key=lambda x: x["domain"])
        return results

    def save_domain_report(self, results: List[Dict], output_path: str) -> None:
        """
        Save domain analysis results to JSON file

        Args:
            results: List of domain analysis results
            output_path: Path to save the report
        """
        report = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_domains": len(results),
                "description": "Domain analysis report from Million Dollar Homepage pixel data",
            },
            "summary": self._generate_summary(results),
            "domains": results,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("Domain report saved to: %s", output_path)

    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from analysis results"""
        if not results:
            return {}

        dns_stats: Dict[str, int] = {}
        http_stats: Dict[str, int] = {}
        whois_stats: Dict[str, int] = {}

        for result in results:
            # DNS statistics
            dns_status = result["dns_status"]
            dns_stats[dns_status] = dns_stats.get(dns_status, 0) + 1

            # HTTP statistics
            http_status = result["http_status"]
            if http_status == 0:
                http_key = "unreachable"
            elif 200 <= http_status < 300:
                http_key = "success"
            elif 300 <= http_status < 400:
                http_key = "redirect"
            elif 400 <= http_status < 500:
                http_key = "client_error"
            elif 500 <= http_status < 600:
                http_key = "server_error"
            else:
                http_key = "other"

            http_stats[http_key] = http_stats.get(http_key, 0) + 1

            # WHOIS statistics
            whois_status = result["whois_status"]
            whois_stats[whois_status] = whois_stats.get(whois_status, 0) + 1

        return {
            "dns_status_distribution": dns_stats,
            "http_status_distribution": http_stats,
            "whois_status_distribution": whois_stats,
        }


def main():
    """Main function for command-line usage"""
    import argparse  # pylint: disable=import-outside-toplevel
    import os  # pylint: disable=import-outside-toplevel

    parser = argparse.ArgumentParser(description="Analyze domains from pixel data")
    parser.add_argument("input_file", help="Path to pixel data JSON file")
    parser.add_argument(
        "-o", "--output", help="Output directory for reports", default="reports"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=10, help="HTTP timeout in seconds"
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)",
    )
    parser.add_argument(
        "--no-threading",
        action="store_true",
        help="Disable threading (sequential analysis)",
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Initialize analyzer
    analyzer = DomainAnalyzer(timeout=args.timeout, max_workers=args.workers)

    # Analyze domains
    use_threading = not args.no_threading
    results = analyzer.analyze_domains_from_json(
        args.input_file, use_threading=use_threading
    )

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(args.output, f"report_{timestamp}.json")

    # Save report
    analyzer.save_domain_report(results, output_file)

    print(f"Analysis complete! Report saved to: {output_file}")
    print(f"Analyzed {len(results)} domains")


if __name__ == "__main__":
    main()

# Million Dollar Homepage Analyzer

A Python tool to analyze and extract pixel data from the Million Dollar Homepage (http://www.milliondollarhomepage.com/).

## Overview

This project downloads and analyzes the Million Dollar Homepage, extracting pixel area data from the HTML map elements and generating structured JSON output with statistics about domains, pixel allocations, and area mappings.

## Features

- Downloads the Million Dollar Homepage HTML
- Extracts pixel area data from HTML map elements
- Generates comprehensive JSON output with metadata and statistics
- Calculates domain statistics and pixel distributions
- Provides timestamped output files
- **Domain Analysis**: Analyzes domains for DNS status, HTTP availability, and WHOIS registration
- **Comprehensive Reports**: Generates detailed domain analysis reports with status summaries

## Installation

```bash
git clone https://github.com/yourusername/million-dollar-homepage-analyzer.git
cd million-dollar-homepage-analyzer
pip install -r requirements.txt
```

## Usage

### Basic Pixel Analysis

```bash
python -m mdh_analyzer
```

This will:
1. Download the Million Dollar Homepage as `web.html`
2. Extract pixel data from the HTML map areas
3. Generate a timestamped JSON file with the format `pixel_data_{timestamp}.json`

### Domain Analysis

Analyze domains from existing pixel data:

```bash
python -m mdh_analyzer analyze-domains data/pixel_data_20251112_202426.json
```

Or use the Python API:

```python
from mdh_analyzer import DomainAnalyzer

analyzer = DomainAnalyzer()
domains = analyzer.extract_domains_from_json("data/pixel_data_20251112_202426.json")
results = [analyzer.analyze_domain(domain) for domain in domains]
analyzer.save_domain_report(results)
```

### Advanced Usage

```python
from mdh_analyzer import MillionDollarAnalyzer

analyzer = MillionDollarAnalyzer()
data = analyzer.analyze()
analyzer.save_json(data, "custom_output.json")
```

### Command Line Interface

The package provides a comprehensive CLI:

```bash
# Analyze pixels with custom URL and output directory
python -m mdh_analyzer analyze-pixels --url http://example.com --output-dir custom_data/

# Analyze domains with verbose output
python -m mdh_analyzer domains data/pixel_data.json --output-dir reports/ --verbose

# Generate markdown report from pixel and domain data
python -m mdh_analyzer report data/pixel_data.json reports/report_20251112_205048.json

# Get help
python -m mdh_analyzer --help
```

## Output Format

### Pixel Data Output

The generated JSON file contains:

- **metadata**: Information about the extraction process
- **summary_statistics**: Aggregate statistics about domains and pixels
- **domains**: Detailed breakdown of each domain with their pixel areas

Example structure:
```json
{
  "metadata": {
    "generated_at": "2025-11-12T19:57:49.506022",
    "source_file": "web.html",
    "description": "Million Dollar Homepage pixel data extraction",
    "total_pixels": 1002800,
    "total_unique_domains": 2822,
    "total_areas": 3306
  },
  "summary_statistics": {
    "largest_domain_by_pixels": "Pending Order",
    "largest_domain_pixels": 18900,
    "average_pixels_per_domain": 355.35,
    "average_pixels_per_area": 303.33
  },
  "domains": [...]
}
```

### Domain Analysis Output

Domain analysis reports are saved to the `reports/` folder with the format `report_{timestamp}.json`:

```json
{
  "metadata": {
    "generated_at": "2025-11-12T20:15:30.123456",
    "description": "Million Dollar Homepage domain analysis",
    "total_domains": 2795
  },
  "summary_statistics": {
    "total_domains": 2795,
    "dns_noerror": 1234,
    "dns_nxdomain": 987,
    "dns_timeout": 45,
    "dns_error": 529,
    "http_success": 1156,
    "http_client_error": 234,
    "http_server_error": 89,
    "http_timeout": 567,
    "http_connection_error": 749,
    "whois_registered": 1890,
    "whois_available": 456,
    "whois_unknown": 449
  },
  "domains": [
    {
      "domain": "example.com",
      "dns_status": "NOERROR",
      "http_status": 200,
      "whois_status": "registered"
    }
  ]
}
```

#### Status Codes Explained

**DNS Status:**
- `NOERROR`: Domain resolves successfully
- `NXDOMAIN`: Domain does not exist
- `TIMEOUT`: DNS query timed out
- `ERROR`: Other DNS resolution error

**HTTP Status:**
- `200`, `301`, `404`, etc.: Standard HTTP status codes
- `TIMEOUT`: HTTP request timed out
- `CONNECTION_ERROR`: Could not connect to server
- `SSL_ERROR`: SSL/TLS certificate error

**WHOIS Status:**
- `registered`: Domain is registered
- `available`: Domain is available for registration
- `unknown`: Could not determine registration status

### Markdown Report Output

Comprehensive markdown reports are generated combining pixel data and domain analysis:

```markdown
# Million Dollar Homepage - Domain Analysis Report

**Analysis Date:** November 12, 2025 at 19:50 UTC
**Source Data:** web.html

## 📊 Executive Summary

This report analyzes **2,795 unique domains** found across **1,002,800 pixels** in **3,306 areas** of the Million Dollar Homepage.

### Key Findings:

- 🟢 **1,890 domains (67.6%)** are registered and potentially active
- 🔴 **456 domains (16.3%)** no longer exist (NXDOMAIN)
- 🟡 **449 domains (16.1%)** are available for purchase
- 💰 **125,400 pixels** are associated with available domains

## 🛒 Available Domains for Purchase

**449 domains** are available for purchase, representing **125,400 pixels** of the Million Dollar Homepage.

### Top Available Domains by Pixel Count

| Domain | Pixels | DNS Status | HTTP Status |
|--------|--------|------------|-------------|
| `example-domain.com` | 2,500 | NXDOMAIN | 0 |
| `another-available.net` | 1,800 | NXDOMAIN | 0 |
```

The markdown reports include:
- **Executive Summary**: Key statistics and findings
- **Domain Status Analysis**: Detailed breakdowns by DNS, HTTP, and WHOIS status
- **Available Domains**: Sorted by pixel count for investment opportunities
- **NXDOMAIN Analysis**: Domains that no longer exist
- **Top Active Domains**: Largest registered domains still active
- **Technical Details**: Analysis methodology and data sources

## Project Structure

```
million-dollar-homepage-analyzer/
├── .github/
│   └── workflows/
│       ├── monthly-analysis.yml           # Monthly pixel analysis
│       ├── daily-domain-analysis.yml      # Daily domain analysis
│       └── README.md
├── data/
│   └── pixel_data_YYYYMMDD_HHMMSS.json
├── reports/
│   ├── report_YYYYMMDD_HHMMSS.json        # Domain analysis data
│   └── report_YYYYMMDD_HHMMSS.md          # Markdown report
├── mdh_analyzer/
│   ├── __init__.py
│   ├── __main__.py                        # CLI entry point
│   ├── analyzer.py                        # Core pixel analysis
│   ├── cli.py                             # Command-line interface
│   ├── domain_analyzer.py                 # Domain analysis module
│   ├── downloader.py                      # Web downloading
│   └── parser.py                          # HTML parsing
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py                   # Pixel analysis tests
│   └── test_domain_analyzer.py            # Domain analysis tests
├── examples/
│   └── sample_output.json
├── requirements.txt                       # Dependencies
├── setup.py                               # Package setup
├── README.md                              # Documentation
├── LICENSE                                # MIT License
└── .gitignore                             # Git ignore rules
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml
- dnspython (for domain analysis)
- python-whois (for domain analysis)

## Automated Analysis Workflows

This repository includes two GitHub Actions for automated analysis:

### 1. Monthly Pixel Analysis
Automatically downloads and analyzes the Million Dollar Homepage for pixel data.

**Features:**
- **Schedule**: Runs on the 1st of each month at 12:00 UTC
- **Manual Trigger**: Can be manually triggered from the GitHub Actions tab
- **Data Storage**: Results saved to `data/pixel_data_YYYYMMDD_HHMMSS.json`
- **Version Control**: Automatically commits and pushes new data files

### 2. Daily Domain Analysis
Automatically analyzes domains from the latest pixel data for DNS, HTTP, and WHOIS status.

**Features:**
- **Schedule**: Runs daily at 2:00 AM UTC (after monthly pixel analysis)
- **Smart Detection**: Automatically finds the latest pixel data file in `data/` folder
- **Comprehensive Analysis**: DNS resolution, HTTP status, WHOIS registration
- **Report Generation**: Results saved to `reports/report_YYYYMMDD_HHMMSS.json` and `reports/report_YYYYMMDD_HHMMSS.md`
- **Manual Trigger**: Can be manually triggered from the GitHub Actions tab

### Viewing Historical Data:
- **Pixel Data**: Check the `data/` folder for historical pixel analysis files
- **Domain Reports**: Check the `reports/` folder for domain analysis reports (JSON data and markdown summaries)
- Each file contains a complete snapshot with timestamps for tracking changes over time
- Markdown reports provide human-readable summaries with available domains sorted by pixel value

## Domain Analysis Features

The domain analyzer provides comprehensive analysis of all domains found in the pixel data:

### DNS Resolution Check
- Verifies if domains resolve to IP addresses
- Identifies non-existent domains (NXDOMAIN)
- Handles DNS timeouts and errors

### HTTP Status Check
- Performs HEAD requests to check website availability
- Returns standard HTTP status codes (200, 404, 500, etc.)
- Handles connection errors, timeouts, and SSL issues
- Tests both HTTP and HTTPS protocols

### WHOIS Registration Check
- Determines if domains are registered or available
- Provides registration status information
- Handles WHOIS query errors gracefully

### Use Cases
- **Domain Portfolio Analysis**: Understand which domains are still active
- **Website Availability**: Check which Million Dollar Homepage links still work
- **Domain Research**: Identify available domains from the historical data
- **Data Quality**: Validate domain data integrity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## About the Million Dollar Homepage

The Million Dollar Homepage was created by Alex Tew in 2005 as a way to raise money for university. The website consists of a 1000×1000 pixel grid, with each pixel sold for $1. This analyzer helps understand the distribution and organization of these pixel purchases.
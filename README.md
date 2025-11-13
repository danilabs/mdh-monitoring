# MDH Monitoring - Million Dollar Homepage Analysis & Monitoring

[![Code Quality & Security](https://github.com/danilabs/mdh-monitoring/actions/workflows/ci.yml/badge.svg)](https://github.com/danilabs/mdh-monitoring/actions/workflows/ci.yml)
[![Daily Domain Analysis](https://github.com/danilabs/mdh-monitoring/actions/workflows/daily-domain-analysis.yml/badge.svg)](https://github.com/danilabs/mdh-monitoring/actions/workflows/daily-domain-analysis.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A comprehensive monitoring and analysis tool for the Million Dollar Homepage** - Track pixel data, monitor domain health, and analyze historical changes over time.

## 🎯 Overview

MDH Monitoring is a sophisticated Python toolkit designed to continuously monitor and analyze the Million Dollar Homepage (http://www.milliondollarhomepage.com/). This project goes beyond simple data extraction to provide comprehensive domain health monitoring, historical trend analysis, and automated reporting capabilities.

**Key Capabilities:**
- **Pixel Data Extraction**: Parse HTML map elements to extract detailed pixel area information
- **Domain Health Monitoring**: Automated DNS, HTTP, and WHOIS status checking for all domains
- **Historical Tracking**: Track changes over time with timestamped data snapshots
- **Automated Reporting**: Generate comprehensive markdown and JSON reports
- **CI/CD Integration**: Automated daily analysis with GitHub Actions workflows

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
git clone https://github.com/danilabs/mdh-monitoring.git
cd mdh-monitoring
pip install -r requirements.txt
```

### Development Installation

For development with all testing and linting tools:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Or use the provided Makefile:

```bash
make dev-setup
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

## 📁 Project Structure

```
mdh-monitoring/
├── .github/
│   └── workflows/
│       ├── ci.yml                         # Code quality & security pipeline
│       └── daily-domain-analysis.yml      # Automated daily domain analysis
├── data/
│   └── pixel_data_YYYYMMDD_HHMMSS.json   # Historical pixel data snapshots
├── reports/
│   ├── report_YYYYMMDD_HHMMSS.json       # Domain analysis data (JSON)
│   └── report_YYYYMMDD_HHMMSS.md         # Human-readable reports (Markdown)
├── mdh_analyzer/                          # Core analysis package
│   ├── __init__.py                        # Package initialization
│   ├── __main__.py                        # CLI entry point
│   ├── analyzer.py                        # Core pixel analysis engine
│   ├── cli.py                             # Command-line interface
│   ├── domain_analyzer.py                 # Domain health monitoring
│   ├── downloader.py                      # Web content retrieval
│   ├── parser.py                          # HTML parsing utilities
│   └── report_generator.py                # Report generation
├── tests/                                 # Test suite
│   ├── __init__.py
│   ├── test_analyzer.py                   # Pixel analysis tests
│   └── test_domain_analyzer.py            # Domain analysis tests
├── requirements.txt                       # Production dependencies
├── requirements-dev.txt                   # Development dependencies
├── setup.py                               # Package configuration
├── pytest.ini                             # Test configuration
├── Makefile                               # Development automation
├── README.md                              # Project documentation
├── LICENSE                                # MIT License
├── STATS.md                               # Project statistics
└── .gitignore                             # Git ignore rules
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml
- dnspython (for domain analysis)
- python-whois (for domain analysis)

## 🤖 Automated Analysis Workflows

MDH Monitoring includes sophisticated GitHub Actions workflows for continuous monitoring and quality assurance:

### 1. 🔍 Code Quality & Security Pipeline (`ci.yml`)
**Comprehensive quality assurance** that runs on every push and pull request to ensure code reliability and security.

**Pipeline Components:**
- **🧪 Unit Tests & Coverage**: Pytest with coverage analysis and Codecov integration
- **📝 Code Quality Analysis**: Pylint with configurable scoring (minimum 7.0/10)
- **🔒 Security Vulnerability Assessment**: Bandit security scanning with critical issue blocking
- **🔤 Static Type Analysis**: MyPy type checking for better code documentation
- **📋 Automated PR Annotations**: Inline code review comments for quality issues

**Quality Standards:**
- Minimum test coverage requirements
- No high/critical security vulnerabilities allowed
- Consistent code formatting and style enforcement
- Cross-platform compatibility testing

### 2. 🌐 Automated Daily Domain Analysis (`daily-domain-analysis.yml`)
**Intelligent domain health monitoring** that automatically analyzes all domains from the latest pixel data.

**Smart Features:**
- **⏰ Scheduled Execution**: Runs daily at 2:00 AM UTC for consistent monitoring
- **🔍 Auto-Discovery**: Automatically locates the most recent pixel data file
- **⚡ High-Performance Processing**: Multi-threaded analysis with 20 concurrent workers
- **📊 Comprehensive Health Checks**: DNS resolution, HTTP availability, WHOIS registration
- **📝 Dual Report Generation**: Both JSON data files and human-readable markdown reports
- **💾 Automated Commit**: Results automatically committed to repository with detailed metadata
- **🎯 Manual Trigger Support**: Can be manually executed from GitHub Actions interface

**Analysis Capabilities:**
- DNS status verification (NOERROR, NXDOMAIN, timeouts)
- HTTP availability testing with status code analysis
- WHOIS registration status checking
- Progress tracking with detailed execution summaries
- Error handling and timeout management (15-second timeout per domain)

### Viewing Historical Data:
- **Pixel Data**: Check the `data/` folder for historical pixel analysis files
- **Domain Reports**: Check the `reports/` folder for domain analysis reports (JSON data and markdown summaries)
- Each file contains a complete snapshot with timestamps for tracking changes over time
- Markdown reports provide human-readable summaries with available domains sorted by pixel value

## Development

### Local Development Commands

This project includes a Makefile for easy development:

```bash
# Set up development environment
make dev-setup

# Run all CI checks locally
make ci

# Individual commands
make test              # Run tests with coverage
make lint              # Run pylint
make security          # Run security scans
make type-check        # Run type checking
make format            # Format code with black and isort
make clean             # Clean up generated files

# Quick development workflow
make quick-check       # Run lint + test
make pre-commit        # Run all pre-commit checks
```

### Code Quality Standards

This project maintains high code quality standards:

- **Pylint Score**: Minimum 7.0/10
- **Test Coverage**: Minimum 70%
- **Security**: No high/critical vulnerabilities allowed
- **Type Hints**: Encouraged for better code documentation
- **Code Formatting**: Black and isort for consistent style

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
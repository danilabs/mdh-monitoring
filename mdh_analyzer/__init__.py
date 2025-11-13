"""
MDH Monitoring - Million Dollar Homepage Analysis & Monitoring

A comprehensive Python toolkit for monitoring and analyzing the Million Dollar Homepage.
Provides pixel data extraction, domain health monitoring, and automated reporting capabilities.
"""

from .analyzer import MillionDollarAnalyzer
from .domain_analyzer import DomainAnalyzer
from .report_generator import MarkdownReportGenerator

__version__ = "1.0.0"
__author__ = "Danilabs"
__email__ = "hi@42security.io"
__description__ = "Million Dollar Homepage Monitoring & Analysis Tool - Track pixel data, domain health, and historical changes"
__url__ = "https://github.com/danilabs/mdh-monitoring"

__all__ = ["MillionDollarAnalyzer", "DomainAnalyzer", "MarkdownReportGenerator"]

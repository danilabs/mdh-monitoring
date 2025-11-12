"""
Million Dollar Homepage Analyzer

A Python package for analyzing and extracting pixel data from the Million Dollar Homepage.
"""

from .analyzer import MillionDollarAnalyzer
from .domain_analyzer import DomainAnalyzer
from .report_generator import MarkdownReportGenerator

__version__ = "1.0.0"
__author__ = "Million Dollar Homepage Analyzer"
__email__ = "contact@example.com"

__all__ = ["MillionDollarAnalyzer", "DomainAnalyzer", "MarkdownReportGenerator"]
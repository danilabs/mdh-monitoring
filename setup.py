"""
Setup script for Million Dollar Homepage Analyzer
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="million-dollar-homepage-analyzer",
    version="1.0.0",
    author="Million Dollar Homepage Analyzer",
    author_email="contact@example.com",
    description="A Python tool to analyze and extract pixel data from the Million Dollar Homepage",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/million-dollar-homepage-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ]
    },
    entry_points={
        "console_scripts": [
            "mdh-analyzer=mdh_analyzer.analyzer:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="million dollar homepage, web scraping, data analysis, pixel analysis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/million-dollar-homepage-analyzer/issues",
        "Source": "https://github.com/yourusername/million-dollar-homepage-analyzer",
        "Documentation": "https://github.com/yourusername/million-dollar-homepage-analyzer#readme",
    },
)
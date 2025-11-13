"""
Command-line interface for the Million Dollar Homepage Analyzer
"""

import argparse
import os
import sys
from datetime import datetime

from .analyzer import MillionDollarAnalyzer
from .domain_analyzer import DomainAnalyzer
from .report_generator import MarkdownReportGenerator


def analyze_pixels(args):
    """Analyze pixel data from the homepage"""
    try:
        analyzer = MillionDollarAnalyzer(args.url)

        if args.verbose:
            print(f"Downloading and analyzing: {args.url}")

        # Perform analysis
        data = analyzer.analyze(download_fresh=True)

        # Save results
        output_file = analyzer.save_json(data, output_dir=args.output_dir)

        print(f"Pixel analysis complete! Results saved to: {output_file}")

    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_domains(args):
    """Analyze domains from pixel data"""
    try:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
            sys.exit(1)

        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        if args.verbose:
            print(f"Analyzing domains from: {args.input_file}")
            if hasattr(args, "workers"):
                print(f"Using {args.workers} concurrent workers")
            if hasattr(args, "no_threading") and args.no_threading:
                print("Threading disabled - using sequential analysis")

        # Initialize analyzer
        max_workers = getattr(args, "workers", 10)
        analyzer = DomainAnalyzer(timeout=args.timeout, max_workers=max_workers)

        # Analyze domains
        use_threading = not getattr(args, "no_threading", False)
        results = analyzer.analyze_domains_from_json(
            args.input_file, use_threading=use_threading
        )

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(args.output_dir, f"report_{timestamp}.json")

        # Save report
        analyzer.save_domain_report(results, output_file)

        print(f"Domain analysis complete! Report saved to: {output_file}")
        print(f"Analyzed {len(results)} domains")

    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_report(args):
    """Generate markdown report from pixel and domain data"""
    try:
        if not os.path.exists(args.pixel_data):
            print(
                f"Error: Pixel data file '{args.pixel_data}' not found", file=sys.stderr
            )
            sys.exit(1)

        if not os.path.exists(args.domain_analysis):
            print(
                f"Error: Domain analysis file '{args.domain_analysis}' not found",
                file=sys.stderr,
            )
            sys.exit(1)

        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        if args.verbose:
            print("Generating markdown report from:")
            print(f"  Pixel data: {args.pixel_data}")
            print(f"  Domain analysis: {args.domain_analysis}")

        # Initialize report generator
        generator = MarkdownReportGenerator()

        # Generate custom output filename if not provided
        output_file = args.output
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(args.output_dir, f"report_{timestamp}.md")
        elif not output_file.startswith(args.output_dir):
            output_file = os.path.join(args.output_dir, output_file)

        # Generate report
        report_file = generator.generate_report(
            args.pixel_data, args.domain_analysis, output_file
        )

        print(f"Markdown report generated successfully: {report_file}")

        # Show file size
        if os.path.exists(report_file):
            size = os.path.getsize(report_file)
            print(f"Report size: {size:,} bytes")

    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Million Dollar Homepage Analyzer - Analyze pixel data and domains"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Pixel analysis subcommand
    pixel_parser = subparsers.add_parser(
        "pixels", help="Analyze pixel data from homepage"
    )
    pixel_parser.add_argument(
        "--url",
        default="http://www.milliondollarhomepage.com/",
        help="URL to analyze (default: Million Dollar Homepage)",
    )
    pixel_parser.add_argument(
        "--output-dir",
        default="data",
        help="Output directory for generated files (default: data)",
    )
    pixel_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Domain analysis subcommand
    domain_parser = subparsers.add_parser(
        "domains", help="Analyze domains from pixel data"
    )
    domain_parser.add_argument("input_file", help="Path to pixel data JSON file")
    domain_parser.add_argument(
        "--output-dir",
        default="reports",
        help="Output directory for domain reports (default: reports)",
    )
    domain_parser.add_argument(
        "--timeout", type=int, default=10, help="HTTP timeout in seconds (default: 10)"
    )
    domain_parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)",
    )
    domain_parser.add_argument(
        "--no-threading",
        action="store_true",
        help="Disable threading (sequential analysis)",
    )
    domain_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Report generation subcommand
    report_parser = subparsers.add_parser(
        "report", help="Generate markdown report from pixel and domain data"
    )
    report_parser.add_argument("pixel_data", help="Path to pixel data JSON file")
    report_parser.add_argument(
        "domain_analysis", help="Path to domain analysis JSON file"
    )
    report_parser.add_argument(
        "--output-dir",
        default="reports",
        help="Output directory for markdown reports (default: reports)",
    )
    report_parser.add_argument(
        "--output", "-o", help="Custom output filename (optional)"
    )
    report_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.command == "pixels":
        analyze_pixels(args)
    elif args.command == "domains":
        analyze_domains(args)
    elif args.command == "report":
        generate_report(args)
    elif args.command is None:
        # Default to pixel analysis if no command specified
        # Create a default args object for pixel analysis
        default_args = argparse.Namespace(
            command="pixels",
            url="http://www.milliondollarhomepage.com/",
            output_dir="data",
            verbose=args.verbose,
        )
        analyze_pixels(default_args)
    else:
        # Show help if no command specified
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

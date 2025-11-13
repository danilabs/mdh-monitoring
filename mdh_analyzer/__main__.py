"""
Main entry point for the mdh_analyzer package when run as a module.
"""

from .cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())

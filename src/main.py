"""
Main runner - Backwards compatibility wrapper
DEPRECATED: Use main_india.py instead
This file redirects to main_india.py for backwards compatibility
"""
import os
import sys
import logging
import argparse

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import from new location
from main_india import main as india_main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.warning("DEPRECATED: src/main.py is deprecated. Use src/main_india.py instead.")
logger.warning("This file will be removed in a future version.")


def main(scan_type: str = "both", test_mode: bool = False):
    """
    Wrapper function that redirects to main_india.py

    Args:
        scan_type: "btst", "swing", or "both"
        test_mode: If True, scan only a small subset
    """
    logger.info("Redirecting to main_india.py...")
    return india_main(scan_type, test_mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Scanner (Deprecated - use main_india.py)")
    parser.add_argument(
        "--type",
        choices=["btst", "swing", "both"],
        default="both",
        help="Type of scan to run"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (scan only 10 stocks)"
    )

    args = parser.parse_args()

    main(scan_type=args.type, test_mode=args.test)

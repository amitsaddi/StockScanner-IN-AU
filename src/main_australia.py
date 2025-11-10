"""
Main runner for Australian stock market - Orchestrates daily stock scanning
"""
import os
import sys
import logging
from datetime import datetime
import argparse

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config.australia_config import AustraliaConfig
from markets.australia.swing_scanner import AustraliaSwingScanner, run_australia_swing_scan
from shared.notifier import Notifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(scan_type: str = "swing", test_mode: bool = False):
    """
    Main function to run Australian stock scans

    Args:
        scan_type: "swing" (BTST not applicable for Australian market)
        test_mode: If True, scan only a small subset
    """
    try:
        # Validate config
        AustraliaConfig.validate()

        notifier = Notifier(AustraliaConfig)

        logger.info(f"Starting {scan_type} scan for AUSTRALIA (test_mode={test_mode})")

        # Track results for summary
        swing_count = 0
        swing_success = True

        # Run Swing scan (only swing for Australian market)
        if scan_type == "swing":
            logger.info("=" * 50)
            logger.info("RUNNING SWING SCAN - AUSTRALIA (ASX 200)")
            logger.info("=" * 50)

            try:
                candidates, report = run_australia_swing_scan(test_mode=test_mode)
                swing_count = len(candidates)

                logger.info(f"Found {swing_count} Australian swing candidates")

                # Send notification if candidates found
                if candidates:
                    notifier.notify_swing_results(report, swing_count)
                    logger.info("Swing notification sent")
                else:
                    logger.info("No Australian swing candidates found")

            except Exception as e:
                swing_success = False
                logger.error(f"Swing scan failed: {e}", exc_info=True)
                notifier.notify_error(f"Australian swing scan failed: {str(e)}")

        logger.info("=" * 50)
        logger.info("SCAN COMPLETE - AUSTRALIA")
        logger.info("=" * 50)

        # Always send completion summary to Telegram
        send_completion_summary(notifier, swing_count, swing_success)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        try:
            notifier = Notifier(AustraliaConfig)
            notifier.notify_error(f"Fatal error in Australian scanner: {str(e)}")
        except:
            pass
        sys.exit(1)


def send_completion_summary(notifier, swing_count, swing_success):
    """Send scan completion summary to Telegram"""
    from datetime import datetime
    import pytz

    # Use Australian Eastern Time
    tz = pytz.timezone('Australia/Sydney')
    timestamp = datetime.now(tz).strftime('%d %b %Y, %I:%M %p AEST')

    summary = f"<b>Stock Scanner - AUSTRALIA - Scan Complete</b>\n"
    summary += f"<i>{timestamp}</i>\n\n"

    if swing_success:
        summary += f"<b>Swing Scan (ASX 200):</b> {swing_count} stocks found\n"
    else:
        summary += f"<b>Swing Scan:</b> Failed\n"

    summary += "\n"

    if swing_count == 0 and swing_success:
        summary += "<i>No trading opportunities found today.</i>\n"
        summary += "The scanner ran successfully but market conditions didn't meet our criteria."
    elif swing_count > 0:
        summary += "<i>Detailed reports sent via email.</i>"

    # Always send to Telegram for completion status
    if notifier.config.SEND_TELEGRAM:
        notifier.send_telegram(summary)
        logger.info("Completion summary sent to Telegram")
    else:
        logger.info("Telegram disabled - completion summary not sent")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Australian Stock Scanner (ASX 200)")
    parser.add_argument(
        "--type",
        choices=["swing"],
        default="swing",
        help="Type of scan to run (only swing available for Australia)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (scan only 10 stocks)"
    )

    args = parser.parse_args()

    main(scan_type=args.type, test_mode=args.test)

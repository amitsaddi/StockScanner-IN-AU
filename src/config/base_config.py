"""
Base configuration - Shared settings across all markets
"""
import os
from dataclasses import dataclass


@dataclass
class TechnicalParams:
    """Technical analysis parameters"""
    ema_short: int = 20
    ema_medium: int = 50
    sma_long: int = 200
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    volume_lookback: int = 20


class BaseConfig:
    """Base configuration shared across all markets"""

    # Environment
    ENV = os.getenv("ENV", "production")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Data source
    DATA_SOURCE = os.getenv("DATA_SOURCE", "yfinance")

    # Notification settings
    SEND_EMAIL = os.getenv("SEND_EMAIL", "True").lower() == "true"
    SEND_TELEGRAM = os.getenv("SEND_TELEGRAM", "False").lower() == "true"

    # Email configuration
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    EMAIL_TO = os.getenv("EMAIL_TO", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

    # Telegram configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # GitHub configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "")

    # Technical parameters
    TECHNICAL = TechnicalParams()

    # File paths
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    RESULTS_DIR = os.path.join(DATA_DIR, "results")

    # Rate limiting
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "2.0"))
    BATCH_SIZE = 50

    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []

        if cls.SEND_EMAIL:
            if not cls.EMAIL_FROM:
                errors.append("EMAIL_FROM not set")
            if not cls.EMAIL_TO:
                errors.append("EMAIL_TO not set")
            if not cls.EMAIL_PASSWORD:
                errors.append("EMAIL_PASSWORD not set")

        if cls.SEND_TELEGRAM:
            if not cls.TELEGRAM_BOT_TOKEN:
                errors.append("TELEGRAM_BOT_TOKEN not set")
            if not cls.TELEGRAM_CHAT_ID:
                errors.append("TELEGRAM_CHAT_ID not set")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

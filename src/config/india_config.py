"""
India market configuration
"""
import os
from dataclasses import dataclass
from .base_config import BaseConfig


@dataclass
class BTSTCriteria:
    """BTST scanning criteria for Indian market"""
    min_gain_percent: float = 2.0
    max_gain_percent: float = 3.5
    min_volume_multiplier: float = 1.5
    min_delivery_percent: float = 40.0
    scan_time: str = "15:15"  # 3:15 PM IST
    max_results: int = 10


@dataclass
class SwingCriteria:
    """Swing trading criteria for Indian market"""
    min_market_cap: float = 5000  # crores
    max_debt_to_equity: float = 0.5
    min_roe: float = 15.0
    rsi_min: int = 40
    rsi_max: int = 60
    min_volume_multiplier: float = 1.2
    max_results: int = 15


class IndiaConfig(BaseConfig):
    """India market specific configuration"""

    # Stock universe
    NIFTY_500_URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

    # Scanning criteria
    BTST = BTSTCriteria()
    SWING = SwingCriteria()

    # File paths
    NIFTY500_FILE = os.path.join(BaseConfig.DATA_DIR, "nifty500.csv")
    RESULTS_DIR = os.path.join(BaseConfig.DATA_DIR, "results", "india")

    # Market hours (IST)
    MARKET_OPEN = "09:15"
    MARKET_CLOSE = "15:30"


# Exclude sectors for BTST (too volatile or news-driven)
BTST_EXCLUDED_SECTORS = [
    "IT",
    "PHARMA"
]

# Preferred sectors for swing trading (Nov 2025)
SWING_PREFERRED_SECTORS = [
    "DEFENCE",
    "CAPITAL GOODS",
    "INFRASTRUCTURE",
    "PSU BANKS",
    "RENEWABLE ENERGY"
]

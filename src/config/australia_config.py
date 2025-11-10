"""
Australia market configuration
"""
import os
from dataclasses import dataclass
from .base_config import BaseConfig


@dataclass
class AustraliaSwingCriteria:
    """Swing trading criteria for Australian market"""
    min_market_cap: float = 50000  # A$500M in lakhs (500M / 10000)
    max_debt_to_equity: float = 1.0
    min_roe: float = 10.0
    rsi_min: float = 35.0
    rsi_max: float = 65.0
    min_52w_high_proximity: float = 85.0
    max_52w_high_proximity: float = 98.0
    min_volume_ratio: float = 1.2
    max_results: int = 15

    # Sector weights for rotation (multiplier applied to score)
    sector_weights = {
        'Materials': 1.2,
        'Energy': 1.15,
        'Financials': 1.0,
        'Consumer Discretionary': 1.0,
        'Industrials': 1.0,
        'Information Technology': 0.8,
        'Health Care': 0.9,
        'Communication Services': 0.85,
        'Consumer Staples': 0.95,
        'Utilities': 0.9,
        'Real Estate': 0.85,
    }


class AustraliaConfig(BaseConfig):
    """Australia market specific configuration"""

    # Stock universe - ASX 200 components
    # Static list as web scraping from asx200list.com may be unreliable
    ASX_200_SYMBOLS = [
        # Top 50 by market cap
        "BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "WBC.AX", "ANZ.AX", "WES.AX", "MQG.AX",
        "FMG.AX", "RIO.AX", "GMG.AX", "WDS.AX", "TCL.AX", "WOW.AX", "TLS.AX", "ALL.AX",
        "NCM.AX", "STO.AX", "RHC.AX", "COL.AX", "QBE.AX", "WTC.AX", "REA.AX", "CPU.AX",
        "IAG.AX", "AMP.AX", "ORG.AX", "S32.AX", "SUN.AX", "SCG.AX", "APA.AX", "CGF.AX",
        "ASX.AX", "TAH.AX", "JHX.AX", "NXT.AX", "DXS.AX", "MGR.AX", "LLC.AX", "SDF.AX",
        "ALD.AX", "GPT.AX", "QAN.AX", "MIN.AX", "BOQ.AX", "EVN.AX", "SYD.AX", "ALX.AX",
        "REH.AX", "ILU.AX",
        # Additional ASX 200 stocks
        "BEN.AX", "BXB.AX", "CAR.AX", "CHC.AX", "CIP.AX", "CLW.AX", "CMW.AX", "COH.AX",
        "CTD.AX", "DHG.AX", "DOW.AX", "DRR.AX", "EDV.AX", "ELD.AX", "FLT.AX", "FPH.AX",
        "GOR.AX", "GUD.AX", "HLS.AX", "HMC.AX", "HUB.AX", "IEL.AX", "IGO.AX", "IFL.AX",
        "IPL.AX", "JBH.AX", "JHG.AX", "LNK.AX", "LOV.AX", "LTR.AX", "LYC.AX", "MAH.AX",
        "MFG.AX", "MP1.AX", "MPL.AX", "NHC.AX", "NHF.AX", "NST.AX", "NWL.AX", "ORI.AX",
        "OSH.AX", "OZL.AX", "PDL.AX", "PLS.AX", "PME.AX", "PNI.AX", "PRU.AX", "PTM.AX",
        "RFF.AX", "RMD.AX", "RRL.AX", "RWC.AX", "SAR.AX", "SEK.AX", "SGM.AX", "SGP.AX",
        "SHL.AX", "SKI.AX", "SPK.AX", "STO.AX", "SVW.AX", "TAH.AX", "TWE.AX", "VCX.AX",
        "VEA.AX", "WHC.AX", "WOR.AX", "WSA.AX", "XRO.AX", "Z1P.AX"
    ]

    # Scanning criteria
    SWING = AustraliaSwingCriteria()

    # File paths
    ASX200_FILE = os.path.join(BaseConfig.DATA_DIR, "asx200.csv")
    RESULTS_DIR = os.path.join(BaseConfig.DATA_DIR, "results", "australia")

    # Market hours (AEST)
    MARKET_OPEN = "10:00"
    MARKET_CLOSE = "16:00"

    # Timezone
    TIMEZONE = "Australia/Sydney"

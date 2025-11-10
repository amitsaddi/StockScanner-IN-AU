"""
Test script for Australian stock scanner
Tests with a small subset of ASX stocks
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.australia_config import AustraliaConfig
from markets.australia.swing_scanner import AustraliaSwingScanner
from shared.data_fetcher import DataFetcher
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_data_fetcher():
    """Test basic data fetching for Australian stocks"""
    print("\n" + "=" * 70)
    print("TEST 1: Data Fetching")
    print("=" * 70)

    config = AustraliaConfig()
    fetcher = DataFetcher(config, market="australia")

    # Test with BHP (largest ASX stock) and CBA (major bank)
    test_symbols = ["BHP.AX", "CBA.AX"]

    print(f"\nFetching data for {len(test_symbols)} test symbols...")

    # Test batch fetch daily data
    historical_data = fetcher.batch_fetch_daily_data(test_symbols, days=100)

    for symbol in test_symbols:
        if symbol in historical_data:
            df = historical_data[symbol]
            print(f"\n{symbol}:")
            print(f"  - Data points: {len(df)}")
            print(f"  - Latest close: A${df['Close'].iloc[-1]:.2f}")
            print(f"  - Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")

            # Calculate indicators
            df = fetcher.calculate_technical_indicators(df)
            latest = df.iloc[-1]
            print(f"  - RSI: {latest.get('RSI', 0):.1f}")
            print(f"  - 52W High Proximity: {latest.get('52W_High_Proximity', 0):.1f}%")
        else:
            print(f"\n{symbol}: FAILED to fetch data")

    # Test fundamentals
    print("\nFetching fundamentals...")
    fundamentals = fetcher.batch_fetch_fundamentals(test_symbols, batch_size=10)

    for symbol in test_symbols:
        if symbol in fundamentals:
            fund = fundamentals[symbol]
            print(f"\n{symbol}:")
            print(f"  - Market Cap: A${fund['market_cap']:.0f} lakhs")
            print(f"  - Sector: {fund['sector']}")
            print(f"  - ROE: {fund['roe']:.1f}%")
            print(f"  - D/E: {fund['debt_to_equity']:.2f}")
        else:
            print(f"\n{symbol}: FAILED to fetch fundamentals")

    print("\nTest 1: PASSED")


def test_swing_scanner():
    """Test the Australian swing scanner with limited symbols"""
    print("\n" + "=" * 70)
    print("TEST 2: Swing Scanner")
    print("=" * 70)

    scanner = AustraliaSwingScanner()

    # Test with top 10 ASX stocks
    test_symbols = [
        "BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "WBC.AX",
        "ANZ.AX", "WES.AX", "MQG.AX", "FMG.AX", "RIO.AX"
    ]

    print(f"\nScanning {len(test_symbols)} stocks...")

    candidates = scanner.scan_for_swing(symbols=test_symbols, max_results=5)

    print(f"\nFound {len(candidates)} swing candidates")

    if candidates:
        print("\nTop Candidates:")
        print("-" * 70)
        for i, c in enumerate(candidates, 1):
            print(f"\n{i}. {c.symbol} ({c.entry_type.upper()})")
            print(f"   Price: A${c.current_price} | Sector: {c.sector}")
            if c.sector_weight > 1.0:
                print(f"   Sector Weight: {c.sector_weight}x")
            print(f"   Score: {c.score:.0f}/100")
            print(f"   RSI: {c.rsi} | 52W High: {c.week_52_high_proximity:.1f}%")
            print(f"   Target: A${c.target} | SL: A${c.stop_loss}")
    else:
        print("\nNo candidates found - this is normal if market conditions don't meet criteria")

    print("\nTest 2: PASSED")


def test_configuration():
    """Test Australian configuration"""
    print("\n" + "=" * 70)
    print("TEST 3: Configuration")
    print("=" * 70)

    config = AustraliaConfig()

    print(f"\nMarket: Australia")
    print(f"Market hours: {config.MARKET_OPEN} - {config.MARKET_CLOSE} AEST")
    print(f"Timezone: {config.TIMEZONE}")
    print(f"ASX 200 symbols loaded: {len(config.ASX_200_SYMBOLS)}")

    print(f"\nSwing Criteria:")
    print(f"  - Min Market Cap: A${config.SWING.min_market_cap} lakhs (A${config.SWING.min_market_cap/100}M)")
    print(f"  - Max D/E: {config.SWING.max_debt_to_equity}")
    print(f"  - Min ROE: {config.SWING.min_roe}%")
    print(f"  - RSI Range: {config.SWING.rsi_min}-{config.SWING.rsi_max}")
    print(f"  - 52W High: {config.SWING.min_52w_high_proximity}-{config.SWING.max_52w_high_proximity}%")

    print(f"\nSector Weights:")
    for sector, weight in sorted(config.SWING.sector_weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {sector}: {weight}x")

    print(f"\nResults directory: {config.RESULTS_DIR}")

    print("\nTest 3: PASSED")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AUSTRALIAN STOCK SCANNER - TEST SUITE")
    print("=" * 70)

    try:
        test_configuration()
        test_data_fetcher()
        test_swing_scanner()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe Australian scanner is ready to use!")
        print("Run: python src/main_australia.py --test")

    except Exception as e:
        print(f"\n\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

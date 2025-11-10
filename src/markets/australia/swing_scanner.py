"""
Australia Swing Trading Scanner - Identifies swing trading opportunities in ASX 200
"""
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

from config.australia_config import AustraliaConfig
from shared.data_fetcher import DataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AustraliaSwingCandidate:
    """Data class for Australian swing trading candidate"""
    symbol: str
    current_price: float
    market_cap: float
    sector: str
    rsi: float
    macd_signal: str
    ema_alignment: bool
    volume_ratio: float
    debt_to_equity: float
    roe: float
    week_52_high_proximity: float
    score: float
    sector_weight: float
    entry_type: str
    target: float
    stop_loss: float
    reason: str


class AustraliaSwingScanner:
    """Scanner for Australian swing trading opportunities"""

    def __init__(self):
        self.config = AustraliaConfig()
        self.fetcher = DataFetcher(self.config, market="australia")
        self.criteria = self.config.SWING

    def check_swing_criteria(self, historical_df: pd.DataFrame,
                            fundamentals: Dict) -> tuple[bool, float, str, str, float]:
        """
        Check if stock meets Australian swing trading criteria

        Returns:
            (passes, score, entry_type, reason, sector_weight)
        """
        if historical_df is None or historical_df.empty or len(historical_df) < 50:
            return False, 0, "", "Insufficient data", 1.0

        reasons = []
        score = 0
        entry_type = "none"

        latest = historical_df.iloc[-1]
        prev = historical_df.iloc[-2]

        # 1. Fundamental filters (must pass all)
        market_cap = fundamentals.get('market_cap', 0)
        debt_to_equity = fundamentals.get('debt_to_equity', 999)
        roe = fundamentals.get('roe', 0)
        sector = fundamentals.get('sector', 'Unknown')

        if market_cap < self.criteria.min_market_cap:
            return False, 0, "", f"Market cap too small: A${market_cap:.0f} lakhs", 1.0

        if debt_to_equity > self.criteria.max_debt_to_equity:
            return False, 0, "", f"High debt: {debt_to_equity:.2f}", 1.0

        if roe < self.criteria.min_roe:
            return False, 0, "", f"Low ROE: {roe:.1f}%", 1.0

        reasons.append(f"Fundamentals: MCap A${market_cap:.0f}L, D/E {debt_to_equity:.2f}, ROE {roe:.1f}%")
        score += 15

        # 2. Trend alignment (above all MAs) - 20 points
        ema_20 = latest.get('EMA_20', 0)
        ema_50 = latest.get('EMA_50', 0)
        sma_200 = latest.get('SMA_200', 0)
        close = latest['Close']

        above_all_ma = close > ema_20 > ema_50 > sma_200

        if above_all_ma:
            score += 20
            reasons.append("Above all MAs (strong uptrend)")
        elif close > ema_20 and close > ema_50:
            score += 15
            reasons.append("Above 20/50 EMA (moderate trend)")
        else:
            score += 5
            reasons.append("Not in clear uptrend")

        # 3. RSI check (35-65 for Australia) - 20 points
        rsi = latest.get('RSI', 50)

        if self.criteria.rsi_min <= rsi <= self.criteria.rsi_max:
            score += 20
            reasons.append(f"RSI {rsi:.1f} (ideal range)")
        elif 30 < rsi < 35:
            # Pullback opportunity
            score += 15
            entry_type = "pullback"
            reasons.append(f"RSI {rsi:.1f} (pullback zone)")
        elif rsi > 65:
            score += 5
            reasons.append(f"RSI {rsi:.1f} (approaching overbought)")
        else:
            reasons.append(f"RSI {rsi:.1f}")

        # 4. 52-week high proximity - 15 points (Australian specific)
        week_52_high_prox = latest.get('52W_High_Proximity', 0)

        if self.criteria.min_52w_high_proximity <= week_52_high_prox <= self.criteria.max_52w_high_proximity:
            score += 15
            reasons.append(f"Near 52W high ({week_52_high_prox:.1f}%)")
        elif week_52_high_prox > self.criteria.max_52w_high_proximity:
            score += 8
            reasons.append(f"At 52W high ({week_52_high_prox:.1f}%)")
        else:
            score += 5
            reasons.append(f"52W high prox: {week_52_high_prox:.1f}%")

        # 5. MACD signals - 15 points
        macd = latest.get('MACD', 0)
        macd_signal_val = latest.get('MACD_Signal', 0)
        macd_hist = latest.get('MACD_Hist', 0)
        prev_macd_hist = prev.get('MACD_Hist', 0)

        macd_status = "neutral"
        if macd > macd_signal_val and macd_hist > 0:
            score += 15
            macd_status = "bullish"
            reasons.append("MACD bullish")
            if prev_macd_hist <= 0:  # Fresh crossover
                entry_type = "macd_cross"
        elif macd > macd_signal_val:
            score += 10
            macd_status = "neutral"
            reasons.append("MACD neutral")

        # 6. Volume confirmation - 10 points
        volume_ratio = latest.get('Volume_Ratio', 1.0)

        if volume_ratio >= self.criteria.min_volume_ratio:
            score += 10
            reasons.append(f"Volume {volume_ratio:.1f}x average")
        else:
            score += 5
            reasons.append(f"Volume {volume_ratio:.1f}x")

        # 7. Sector weight application - Get sector weight
        sector_weight = self.criteria.sector_weights.get(sector, 1.0)
        if sector_weight > 1.0:
            reasons.append(f"Sector: {sector} (weight: {sector_weight}x)")
        else:
            reasons.append(f"Sector: {sector}")

        # Detect entry type if not already set
        if entry_type == "none":
            # Check for breakout
            if close > latest.get('EMA_20', 0) * 1.02 and volume_ratio > 1.5:
                entry_type = "breakout"
            # Check for MA crossover
            elif ema_20 > ema_50 and prev.get('EMA_20', 0) <= prev.get('EMA_50', 0):
                entry_type = "ma_cross"
            else:
                entry_type = "trend_follow"

        # Apply sector weight to score
        weighted_score = score * sector_weight

        # Minimum score threshold: 60/100 (before sector weight)
        passes = score >= 60

        return passes, weighted_score, entry_type, "; ".join(reasons), sector_weight

    def calculate_targets(self, current_price: float, entry_type: str) -> tuple[float, float]:
        """
        Calculate target and stop loss based on entry type

        Returns:
            (target, stop_loss)
        """
        if entry_type == "breakout":
            target = current_price * 1.15  # 15% target
            stop_loss = current_price * 0.95  # 5% SL
        elif entry_type == "pullback":
            target = current_price * 1.12  # 12% target
            stop_loss = current_price * 0.93  # 7% SL
        else:  # trend_follow, macd_cross, ma_cross
            target = current_price * 1.15  # 15% target
            stop_loss = current_price * 0.94  # 6% SL

        return round(target, 2), round(stop_loss, 2)

    def scan_for_swing(self, symbols: List[str] = None, max_results: int = None) -> List[AustraliaSwingCandidate]:
        """
        Scan Australian stocks for swing trading opportunities

        Args:
            symbols: List of symbols to scan
            max_results: Maximum results to return

        Returns:
            List of AustraliaSwingCandidate objects sorted by score
        """
        if symbols is None:
            symbols = self.fetcher.get_asx200_symbols()

        if max_results is None:
            max_results = self.criteria.max_results

        logger.info(f"Scanning {len(symbols)} ASX stocks for swing opportunities...")

        # Step 1: Batch fetch fundamentals for all symbols
        logger.info("Step 1/3: Fetching fundamentals...")
        fundamentals_dict = self.fetcher.batch_fetch_fundamentals(symbols, batch_size=50)

        # Step 2: Filter symbols based on fundamental criteria
        logger.info("Step 2/3: Filtering by fundamental criteria...")
        filtered_symbols = []
        for symbol, fundamentals in fundamentals_dict.items():
            if fundamentals.get('market_cap', 0) >= self.criteria.min_market_cap:
                if fundamentals.get('debt_to_equity', 999) <= self.criteria.max_debt_to_equity:
                    filtered_symbols.append(symbol)

        logger.info(f"Found {len(filtered_symbols)} stocks passing fundamental filters")

        if not filtered_symbols:
            logger.info("No stocks meet fundamental criteria")
            return []

        # Step 3: Batch fetch historical data for filtered symbols
        logger.info("Step 3/3: Fetching historical data for filtered stocks...")
        historical_data_dict = self.fetcher.batch_fetch_daily_data(filtered_symbols, days=300)

        # Step 4: Analyze each filtered stock
        logger.info("Analyzing candidates...")
        candidates = []

        for symbol in filtered_symbols:
            try:
                fundamentals = fundamentals_dict.get(symbol)
                historical_df = historical_data_dict.get(symbol)

                if historical_df is None or fundamentals is None:
                    continue

                # Calculate technical indicators
                historical_df = self.fetcher.calculate_technical_indicators(historical_df)

                # Check criteria
                passes, score, entry_type, reason, sector_weight = self.check_swing_criteria(
                    historical_df, fundamentals
                )

                if passes:
                    latest = historical_df.iloc[-1]
                    current_price = latest['Close']

                    target, stop_loss = self.calculate_targets(current_price, entry_type)

                    candidate = AustraliaSwingCandidate(
                        symbol=symbol.replace('.AX', ''),
                        current_price=round(current_price, 2),
                        market_cap=fundamentals['market_cap'],
                        sector=fundamentals['sector'],
                        rsi=round(latest.get('RSI', 0), 1),
                        macd_signal="bullish" if latest.get('MACD', 0) > latest.get('MACD_Signal', 0) else "bearish",
                        ema_alignment=current_price > latest.get('EMA_20', 0) > latest.get('EMA_50', 0),
                        volume_ratio=round(latest.get('Volume_Ratio', 1.0), 1),
                        debt_to_equity=fundamentals['debt_to_equity'],
                        roe=fundamentals['roe'],
                        week_52_high_proximity=round(latest.get('52W_High_Proximity', 0), 1),
                        score=score,
                        sector_weight=sector_weight,
                        entry_type=entry_type,
                        target=target,
                        stop_loss=stop_loss,
                        reason=reason
                    )
                    candidates.append(candidate)
                    logger.info(f"Swing candidate: {candidate.symbol} (score: {score:.0f})")

            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue

        # Sort by weighted score descending
        candidates.sort(key=lambda x: x.score, reverse=True)

        return candidates[:max_results]

    def generate_report(self, candidates: List[AustraliaSwingCandidate]) -> str:
        """Generate text report of Australian swing candidates"""
        if not candidates:
            return "No Australian swing trading candidates found."

        report = f"ASX SWING TRADING WATCHLIST - {datetime.now().strftime('%d %B %Y')}\n"
        report += "=" * 70 + "\n\n"

        for i, c in enumerate(candidates, 1):
            report += f"{i}. {c.symbol} - {c.entry_type.upper()}\n"
            report += f"   Price: A${c.current_price} | Sector: {c.sector}"
            if c.sector_weight > 1.0:
                report += f" (Weight: {c.sector_weight}x)\n"
            else:
                report += "\n"
            report += f"   RSI: {c.rsi} | MACD: {c.macd_signal} | Volume: {c.volume_ratio}x\n"
            report += f"   52W High: {c.week_52_high_proximity:.1f}%\n"
            report += f"   ROE: {c.roe:.1f}% | D/E: {c.debt_to_equity:.2f} | MCap: A${c.market_cap:.0f}L\n"
            report += f"   Target: A${c.target} ({((c.target/c.current_price-1)*100):.1f}%) | SL: A${c.stop_loss}\n"
            report += f"   Score: {c.score:.0f}/100\n"
            report += f"   {c.reason}\n"
            report += "\n"

        report += "SWING TRADING TIPS:\n"
        report += "- Hold for 3-15 days\n"
        report += "- Book 50% at first target, trail rest\n"
        report += "- Exit ruthlessly if SL hit\n"
        report += "- Review positions daily after market close (4:00 PM AEST)\n"

        return report

    def save_results(self, candidates: List[AustraliaSwingCandidate], filename: str = None):
        """Save scan results to CSV"""
        if not candidates:
            logger.info("No candidates to save")
            return

        if filename is None:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"swing_scan_{date_str}.csv"

        import os
        os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(self.config.RESULTS_DIR, filename)

        data = []
        for c in candidates:
            data.append({
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Symbol': c.symbol,
                'Price': c.current_price,
                'Sector': c.sector,
                'Entry_Type': c.entry_type,
                'RSI': c.rsi,
                'Volume_Ratio': c.volume_ratio,
                '52W_High_%': c.week_52_high_proximity,
                'ROE_%': c.roe,
                'Debt_Equity': c.debt_to_equity,
                'Target': c.target,
                'Stop_Loss': c.stop_loss,
                'Score': c.score,
                'Sector_Weight': c.sector_weight
            })

        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        logger.info(f"Results saved to {filepath}")


def run_australia_swing_scan(test_mode: bool = False):
    """Main function to run Australian swing scan"""
    scanner = AustraliaSwingScanner()

    if test_mode:
        symbols = ["BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "WBC.AX",
                   "ANZ.AX", "WES.AX", "MQG.AX", "FMG.AX", "RIO.AX"]
        logger.info("Running in TEST MODE with 10 stocks")
    else:
        symbols = None

    candidates = scanner.scan_for_swing(symbols=symbols)
    report = scanner.generate_report(candidates)
    print("\n" + report)
    scanner.save_results(candidates)

    return candidates, report


if __name__ == "__main__":
    run_australia_swing_scan(test_mode=True)

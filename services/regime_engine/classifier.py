"""
Market AI — Dedicated Indian Market Regime Classifier Engine
Evaluates NIFTY/BANK NIFTY trends, Breadth, India VIX, FII/DII liquidity, and macro variables
to classify the market state into deterministic regime states with confidence & drivers.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from packages.shared_types.market_types import (
    MarketRegime,
    MarketRegimeState,
    MarketBreadth,
    FiiDiiActivity,
    IndexQuote,
)
from packages.market_calendar.calendar import IST_TIMEZONE


class MarketRegimeClassifier:
    """Classifies current Indian macro and market regime state."""

    def evaluate_regime(
        self,
        nifty_quote: IndexQuote,
        bank_nifty_quote: IndexQuote,
        vix_quote: IndexQuote,
        breadth: MarketBreadth,
        fii_dii: FiiDiiActivity,
        usdinr: float = 86.85,
        brent_crude: float = 78.40,
    ) -> MarketRegimeState:
        """Evaluates multivariate quantitative rules to compute market regime."""
        drivers: List[str] = []
        risks: List[str] = []

        # 1. Trend Score (NIFTY & BANK NIFTY)
        nifty_up = nifty_quote.percent_change >= 0
        bank_up = bank_nifty_quote.percent_change >= 0
        if nifty_up and bank_up:
            trend_score = 1.0
            drivers.append(f"Synchronized bullish momentum across NIFTY 50 ({nifty_quote.percent_change:+.2f}%) and BANK NIFTY ({bank_nifty_quote.percent_change:+.2f}%)")
        elif nifty_up or bank_up:
            trend_score = 0.5
            drivers.append("Sector divergence between NIFTY 50 and Banking benchmark")
        else:
            trend_score = 0.0
            risks.append(f"Downward index pressure: NIFTY ({nifty_quote.percent_change:+.2f}%) and BANK NIFTY ({bank_nifty_quote.percent_change:+.2f}%)")

        # 2. Volatility Score (India VIX)
        vix_val = vix_quote.current_value
        if vix_val < 14.0:
            vol_score = 1.0
            drivers.append(f"India VIX at low-anxiety levels ({vix_val:.2f}) promoting structural accumulation")
        elif vix_val < 18.0:
            vol_score = 0.6
            drivers.append(f"India VIX in standard neutral band ({vix_val:.2f})")
        else:
            vol_score = 0.2
            risks.append(f"Elevated India VIX ({vix_val:.2f}) indicating heightened market volatility")

        # 3. Market Breadth Score
        adr = breadth.advance_decline_ratio
        if adr >= 1.3:
            breadth_score = 1.0
            drivers.append(f"Broad-based market participation (Advance/Decline Ratio: {adr:.2f})")
        elif adr >= 0.8:
            breadth_score = 0.5
            drivers.append(f"Neutral market breadth (Advance/Decline Ratio: {adr:.2f})")
        else:
            breadth_score = 0.0
            risks.append(f"Weak market breadth with widespread stock declines (ADR: {adr:.2f})")

        # 4. Institutional Liquidity Score
        total_inst_net = fii_dii.total_institutional_net
        if total_inst_net > 500.0:
            liq_score = 1.0
            drivers.append(f"Net institutional cash market buying: +₹{total_inst_net:,.2f} Cr (FII: ₹{fii_dii.fii_net:,.2f} Cr, DII: ₹{fii_dii.dii_net:,.2f} Cr)")
        elif total_inst_net > -500.0:
            liq_score = 0.5
            drivers.append(f"Balanced institutional cash flows: ₹{total_inst_net:,.2f} Cr")
        else:
            liq_score = 0.0
            risks.append(f"Institutional cash market distribution: ₹{total_inst_net:,.2f} Cr")

        # 5. Global Macro Factors
        if brent_crude > 85.0:
            risks.append(f"Elevated crude oil prices (${brent_crude:.2f}/bbl) pressuring Indian fiscal deficit")
        if usdinr > 87.5:
            risks.append(f"Currency depreciation pressure on USD/INR (₹{usdinr:.2f})")

        # Weighted Probability Calculation
        composite_prob = (
            (trend_score * 0.35)
            + (vol_score * 0.20)
            + (breadth_score * 0.25)
            + (liq_score * 0.20)
        )
        composite_prob = round(float(composite_prob), 2)

        # Classify state
        if vix_val >= 20.0:
            regime = MarketRegime.HIGH_VOLATILITY
        elif composite_prob >= 0.65:
            regime = MarketRegime.BULL
        elif composite_prob <= 0.35:
            regime = MarketRegime.BEAR
        else:
            regime = MarketRegime.RANGE

        confidence = round(0.65 + (abs(composite_prob - 0.5) * 0.5), 2)

        return MarketRegimeState(
            regime=regime,
            probability=max(0.51, composite_prob) if regime == MarketRegime.BULL else max(0.51, 1.0 - composite_prob),
            confidence=confidence,
            drivers=drivers,
            risks=risks,
            updated_at=datetime.now(IST_TIMEZONE),
        )

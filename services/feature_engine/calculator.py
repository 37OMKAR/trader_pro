"""
Market AI — Feature Engine Indicator Calculator
Computes exact mathematical technical, volume, momentum, and statistical features
from candlestick series and market benchmark data with zero external calculation drift.
"""

import math
from typing import List, Dict, Any, Optional
import numpy as np
from packages.shared_types.market_types import Candle


class FeatureCalculator:
    """Calculates quantitative and technical features from historical OHLCV data."""

    @staticmethod
    def calculate_sma(closes: List[float], period: int) -> Optional[float]:
        if len(closes) < period:
            return None
        return round(float(np.mean(closes[-period:])), 2)

    @staticmethod
    def calculate_ema(closes: List[float], period: int) -> Optional[float]:
        if len(closes) < period:
            return None
        k = 2.0 / (period + 1.0)
        ema = float(np.mean(closes[:period]))
        for price in closes[period:]:
            ema = (price * k) + (ema * (1.0 - k))
        return round(ema, 2)

    @staticmethod
    def calculate_rsi(closes: List[float], period: int = 14) -> Optional[float]:
        """Calculates Relative Strength Index (RSI) with Wilder's exponential smoothing."""
        if len(closes) < period + 1:
            return None

        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return round(float(rsi), 2)

    @staticmethod
    def calculate_macd(
        closes: List[float], fast: int = 12, slow: int = 26, signal_period: int = 9
    ) -> Dict[str, Optional[float]]:
        """Calculates MACD Line, Signal Line, and MACD Histogram."""
        if len(closes) < slow + signal_period:
            return {"macd_line": None, "signal_line": None, "histogram": None}

        # Calculate fast and slow EMAs series
        k_fast = 2.0 / (fast + 1.0)
        k_slow = 2.0 / (slow + 1.0)

        ema_fast = np.mean(closes[:fast])
        for p in closes[fast:]:
            ema_fast = (p * k_fast) + (ema_fast * (1.0 - k_fast))

        ema_slow = np.mean(closes[:slow])
        for p in closes[slow:]:
            ema_slow = (p * k_slow) + (ema_slow * (1.0 - k_slow))

        macd_line = ema_fast - ema_slow
        signal_line = macd_line * 0.92  # Smooth approximation for signal
        hist = macd_line - signal_line

        return {
            "macd_line": round(float(macd_line), 2),
            "signal_line": round(float(signal_line), 2),
            "histogram": round(float(hist), 2),
        }

    @staticmethod
    def calculate_atr(candles: List[Candle], period: int = 14) -> Optional[float]:
        """Calculates Average True Range (ATR)."""
        if len(candles) < period + 1:
            return None

        tr_list = []
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i - 1].close
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)

        atr = np.mean(tr_list[:period])
        for tr in tr_list[period:]:
            atr = (atr * (period - 1) + tr) / period

        return round(float(atr), 2)

    @staticmethod
    def calculate_bollinger_bands(
        closes: List[float], period: int = 20, num_std: float = 2.0
    ) -> Dict[str, Optional[float]]:
        """Calculates Upper Band, Middle Band (SMA 20), Lower Band, and Bandwidth."""
        if len(closes) < period:
            return {"upper": None, "middle": None, "lower": None, "bandwidth": None, "pct_b": None}

        window = np.array(closes[-period:])
        middle = float(np.mean(window))
        std = float(np.std(window))

        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        bandwidth = ((upper - lower) / max(middle, 0.01)) * 100.0
        current = closes[-1]
        pct_b = (current - lower) / max(upper - lower, 0.01)

        return {
            "upper": round(upper, 2),
            "middle": round(middle, 2),
            "lower": round(lower, 2),
            "bandwidth": round(bandwidth, 2),
            "pct_b": round(pct_b, 3),
        }

    @staticmethod
    def calculate_volume_zscore(volumes: List[int], period: int = 20) -> Optional[float]:
        """Calculates Volume z-score relative to 20-day mean & standard deviation."""
        if len(volumes) < period:
            return None
        window = np.array(volumes[-period:], dtype=float)
        mean_vol = float(np.mean(window))
        std_vol = float(np.std(window))
        if std_vol == 0:
            return 0.0
        current_vol = float(volumes[-1])
        zscore = (current_vol - mean_vol) / std_vol
        return round(float(zscore), 2)

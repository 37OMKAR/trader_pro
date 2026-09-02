"""
Event triggers that decide when a symbol goes onto the deliberation queue.

Cheap checks over recent candles. Deliberation is expensive; watch is not.
"""

from typing import List, Sequence, Any, Optional
from agents.indicators import sma, rsi, volume_zscore, rolling_return_pct


def fired(candles: Sequence[Any]) -> Optional[str]:
    """Return a short trigger name if a hard signal fired since the last bar, else None.

    Rules (any one triggers):
      - 20DMA cross: today's close crossed the 20DMA vs yesterday's close.
      - RSI extreme: RSI(14) crossed 30 up or 70 down.
      - Volume shock: last-bar volume z-score >= 2.0.
      - Gap: |close-yesterday_close|/yesterday_close > 2%.
      - Momentum: |5-day return| > 5%.
    """
    if len(candles) < 21:
        return None

    prev_close = float(candles[-2].close)
    last_close = float(candles[-1].close)

    s20_prev = sma(candles[:-1], 20)
    s20_now = sma(candles, 20)
    if s20_prev is not None and s20_now is not None:
        if (prev_close < s20_prev and last_close >= s20_now):
            return "SMA20_CROSS_UP"
        if (prev_close > s20_prev and last_close <= s20_now):
            return "SMA20_CROSS_DOWN"

    r_now = rsi(candles, 14)
    r_prev = rsi(candles[:-1], 14) if len(candles) >= 22 else None
    if r_now is not None and r_prev is not None:
        if r_prev >= 30 and r_now < 30:
            return "RSI_OVERSOLD"
        if r_prev <= 70 and r_now > 70:
            return "RSI_OVERBOUGHT"

    vzs = volume_zscore(candles, 20)
    if vzs is not None and vzs >= 2.0:
        return "VOLUME_SHOCK"

    if prev_close > 0 and abs(last_close - prev_close) / prev_close >= 0.02:
        return "GAP_MOVE"

    ret5 = rolling_return_pct(candles, 5)
    if ret5 is not None and abs(ret5) >= 5.0:
        return "MOMENTUM_5D"

    return None

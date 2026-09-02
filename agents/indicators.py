"""
Market AI — Shared indicator math used by every analyst.
Pure functions over a list of Candle objects (uses only .open/.high/.low/.close/.volume).
"""

from typing import List, Sequence, Tuple, Optional, Any
import math


def _closes(candles: Sequence[Any]) -> List[float]:
    return [float(c.close) for c in candles]


def sma(candles: Sequence[Any], period: int) -> Optional[float]:
    if len(candles) < period or period <= 0:
        return None
    xs = _closes(candles)[-period:]
    return round(sum(xs) / period, 4)


def ema(candles: Sequence[Any], period: int) -> Optional[float]:
    if len(candles) < period or period <= 0:
        return None
    xs = _closes(candles)
    k = 2.0 / (period + 1.0)
    val = sum(xs[:period]) / period
    for x in xs[period:]:
        val = x * k + val * (1.0 - k)
    return round(val, 4)


def rsi(candles: Sequence[Any], period: int = 14) -> Optional[float]:
    xs = _closes(candles)
    if len(xs) < period + 1:
        return None
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        d = xs[i] - xs[i - 1]
        if d >= 0:
            gains += d
        else:
            losses -= d
    avg_g = gains / period
    avg_l = losses / period
    for i in range(period + 1, len(xs)):
        d = xs[i] - xs[i - 1]
        g = d if d > 0 else 0.0
        l = -d if d < 0 else 0.0
        avg_g = (avg_g * (period - 1) + g) / period
        avg_l = (avg_l * (period - 1) + l) / period
    if avg_l == 0:
        return 100.0 if avg_g > 0 else 50.0
    rs = avg_g / avg_l
    return round(100.0 - (100.0 / (1.0 + rs)), 2)


def atr(candles: Sequence[Any], period: int = 14) -> Optional[float]:
    if len(candles) < period + 1:
        return None
    trs: List[float] = []
    for i in range(1, len(candles)):
        h = float(candles[i].high)
        l = float(candles[i].low)
        pc = float(candles[i - 1].close)
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    if len(trs) < period:
        return None
    val = sum(trs[:period]) / period
    for tr in trs[period:]:
        val = (val * (period - 1) + tr) / period
    return round(val, 4)


def annualized_volatility(candles: Sequence[Any], period: int = 20, bars_per_year: int = 252) -> Optional[float]:
    xs = _closes(candles)
    if len(xs) < period + 1:
        return None
    rets = [math.log(xs[i] / xs[i - 1]) for i in range(len(xs) - period, len(xs)) if xs[i - 1] > 0]
    if len(rets) < 2:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return round(math.sqrt(var * bars_per_year) * 100.0, 2)


def rolling_return_pct(candles: Sequence[Any], lookback: int) -> Optional[float]:
    xs = _closes(candles)
    if len(xs) < lookback + 1 or xs[-lookback - 1] == 0:
        return None
    return round((xs[-1] / xs[-lookback - 1] - 1.0) * 100.0, 2)


def drawdown_from_peak_pct(candles: Sequence[Any], lookback: int = 60) -> Optional[float]:
    xs = _closes(candles)[-lookback:]
    if not xs:
        return None
    peak = max(xs)
    if peak <= 0:
        return None
    return round((xs[-1] / peak - 1.0) * 100.0, 2)


def volume_zscore(candles: Sequence[Any], period: int = 20) -> Optional[float]:
    if len(candles) < period + 1:
        return None
    vols = [float(c.volume) for c in candles[-(period + 1):]]
    ref = vols[:-1]
    mean = sum(ref) / len(ref)
    var = sum((v - mean) ** 2 for v in ref) / max(1, len(ref) - 1)
    sd = math.sqrt(var) or 1.0
    return round((vols[-1] - mean) / sd, 2)


def support_resistance(candles: Sequence[Any], lookback: int = 30) -> Tuple[Optional[float], Optional[float]]:
    if not candles:
        return None, None
    window = candles[-lookback:]
    lows = [float(c.low) for c in window]
    highs = [float(c.high) for c in window]
    if not lows or not highs:
        return None, None
    return round(min(lows), 2), round(max(highs), 2)


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def normalize_signed(x: float, scale: float) -> float:
    """Squash x/scale into [-1, +1] with tanh."""
    if scale <= 0:
        return 0.0
    return clamp(math.tanh(x / scale))


def detect_regime(candles: Sequence[Any]) -> str:
    """BULL / BEAR / CHOP from SMA alignment + recent return + volatility."""
    s20 = sma(candles, 20)
    s50 = sma(candles, 50)
    ret20 = rolling_return_pct(candles, 20) or 0.0
    if s20 is None or s50 is None:
        return "UNKNOWN"
    if s20 > s50 and ret20 > 2.0:
        return "BULL"
    if s20 < s50 and ret20 < -2.0:
        return "BEAR"
    return "CHOP"

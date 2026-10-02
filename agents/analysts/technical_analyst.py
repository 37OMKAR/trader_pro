"""
Market AI — Technical Analyst Agent
Evaluates moving averages, momentum indicators, breakout zones, and support/resistance.
Computes real SMA 20/50/200 and RSI 14 from the supplied candle series.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient


def _close(c: Any) -> float:
    if isinstance(c, dict):
        return float(c.get("close", 0.0))
    return float(getattr(c, "close", 0.0))


def _sma(closes: List[float], window: int) -> float:
    if not closes:
        return 0.0
    window = min(window, len(closes))
    return round(sum(closes[-window:]) / window, 2)


def _rsi(closes: List[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    gains = 0.0
    losses = 0.0
    for i in range(len(closes) - period, len(closes)):
        delta = closes[i] - closes[i - 1]
        if delta >= 0:
            gains += delta
        else:
            losses -= delta
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return round(100.0 - (100.0 / (1.0 + rs)), 2)


class TechnicalAnalystAgent:
    """Specialized agent analyzing chart patterns and price action."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Technical Analyst"

    async def analyze(
        self, symbol: str, quote_data: Dict[str, Any], candles: List[Any]
    ) -> Dict[str, Any]:
        last_price = float(quote_data.get("last_price", 0.0))

        closes = [_close(c) for c in candles] if candles else []
        if last_price <= 0 and closes:
            last_price = closes[-1]

        if closes:
            sma_20 = _sma(closes, 20)
            sma_50 = _sma(closes, 50)
            sma_200 = _sma(closes, 200)
            rsi_14 = _rsi(closes, 14)
            recent = closes[-min(len(closes), 60):]
            swing_low = round(min(recent), 2)
            swing_high = round(max(recent), 2)
            support_1 = round(max(swing_low, last_price * 0.975), 2)
            support_2 = round(min(swing_low, last_price * 0.95), 2)
            resistance_1 = round(min(swing_high, last_price * 1.035), 2)
            resistance_2 = round(max(swing_high, last_price * 1.06), 2)
            data_source = "candles"
        else:
            sma_20 = round(last_price * 0.985, 2)
            sma_50 = round(last_price * 0.965, 2)
            sma_200 = round(last_price * 0.920, 2)
            rsi_14 = 50.0
            support_1 = round(last_price * 0.975, 2)
            support_2 = round(last_price * 0.950, 2)
            resistance_1 = round(last_price * 1.035, 2)
            resistance_2 = round(last_price * 1.060, 2)
            data_source = "estimated"

        if last_price > sma_20 > sma_50 and sma_50 > sma_200:
            trend = "BULLISH"
        elif last_price < sma_20 < sma_50 and sma_50 < sma_200:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"

        if rsi_14 >= 70:
            momentum = "overbought"
        elif rsi_14 <= 30:
            momentum = "oversold"
        else:
            momentum = "healthy"

        system_prompt = (
            "You are an Institutional Technical Analyst focusing on NSE Indian Equities and Indices. "
            "Analyze candlestick patterns, moving average alignments, RSI, and support/resistance levels."
        )

        user_prompt = (
            f"Analyze technical setup for {symbol}:\n"
            f"- Last Traded Price: ₹{last_price}\n"
            f"- SMA Alignment: 20-DMA (₹{sma_20}), 50-DMA (₹{sma_50}), 200-DMA (₹{sma_200})\n"
            f"- RSI (14): {rsi_14} ({momentum} momentum)\n"
            f"- Key Support: ₹{support_1}, ₹{support_2}\n"
            f"- Key Resistance: ₹{resistance_1}, ₹{resistance_2}\n\n"
            "Provide: 1. Trend Direction, 2. Breakout or Consolidation status, 3. Entry & Stop-loss zones."
        )

        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "trend": trend,
            "indicators": {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "rsi_14": rsi_14,
                "support_1": support_1,
                "support_2": support_2,
                "resistance_1": resistance_1,
                "resistance_2": resistance_2,
            },
            "data_source": data_source,
            "samples_used": len(closes),
            "summary": (
                f"Price ₹{last_price} with 20-DMA ₹{sma_20}, 50-DMA ₹{sma_50}, 200-DMA ₹{sma_200}. "
                f"RSI {rsi_14} indicates {momentum} momentum. Trend classification: {trend}. "
                f"Immediate resistance ₹{resistance_1}, immediate support ₹{support_1}."
            ),
            "llm_commentary": llm_commentary,
        }

"""
Market AI — Neutral Risk Arbiter & Kelly Criterion Judge
Synthesizes the Aggressive and Conservative debate perspectives using Kelly Criterion, India VIX regime metrics, and Sharpe maximization.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class NeutralRiskArbiter:
    """Mathematical arbiter resolving risk debates through statistical expected value and Kelly sizing."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Neutral Risk Arbiter"

    async def arbitrate(
        self,
        symbol: str,
        trade_proposal: Dict[str, Any],
        aggressive_case: Dict[str, Any],
        conservative_case: Dict[str, Any],
        india_vix: float = 14.5,
        win_prob: float = 0.58,
    ) -> Dict[str, Any]:
        entry = trade_proposal.get("entry_price", 1000.0)
        target = trade_proposal.get("target_1", entry * 1.05)
        stop = trade_proposal.get("stop_loss", entry * 0.98)

        risk_pct = max(0.01, (entry - stop) / entry)
        reward_pct = max(0.01, (target - entry) / entry)
        b_ratio = reward_pct / risk_pct  # Odds ratio (b)

        # Full Kelly Criterion: f* = (p * b - q) / b
        q_prob = 1.0 - win_prob
        kelly_fraction = max(0.0, (win_prob * b_ratio - q_prob) / b_ratio)
        
        # Half-Kelly Prudence Sizing (institutional best practice)
        half_kelly_pct = round(min(15.0, (kelly_fraction * 0.5) * 100.0), 1)
        
        # VIX Volatility Penalty: Higher VIX reduces allocation
        vix_multiplier = 1.0 if india_vix < 16.0 else (0.8 if india_vix < 22.0 else 0.6)
        final_allocation_pct = round(max(5.0, half_kelly_pct * vix_multiplier), 1)

        system_prompt = (
            "You are the Chief Quantitative Arbiter & Risk Committee Judge. "
            "Synthesize the Aggressive debator's growth case and the Conservative debator's capital defense case. "
            "Deliver a mathematical verdict on final approved position size and stop-loss rules."
        )

        user_prompt = (
            f"Arbitrate Risk Committee Debate for {symbol}:\n"
            f"- Aggressive View: {aggressive_case.get('argument')}\n"
            f"- Conservative View: {conservative_case.get('argument')}\n"
            f"- Mathematical Kelly Sizing: {half_kelly_pct}% (Adjusted for India VIX {india_vix}: {final_allocation_pct}%)\n\n"
            "State the final Risk Committee consensus verdict and conditions."
        )

        llm_verdict = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "verdict": "CONSENSUS_APPROVED",
            "approved_allocation_pct": final_allocation_pct,
            "kelly_fraction": round(kelly_fraction, 3),
            "vix_adjustment_factor": vix_multiplier,
            "consensus_summary": (
                f"Risk Committee synthesized a balanced compromise: Approved {final_allocation_pct}% capital allocation "
                f"based on Half-Kelly criterion (1:{round(b_ratio, 2)} R:R with {round(win_prob*100)}% base win rate) "
                f"conditioned on India VIX at {india_vix}."
            ),
            "llm_verdict": llm_verdict,
        }

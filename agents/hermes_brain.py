"""
Market AI — Hermes Supervisor Brain & Autonomous Research Orchestrator
Coordinates subagents, conducts TinyFish live web research, runs multi-agent debates,
and synthesizes institutional trading decisions powered by Hermes-3 and DeepSeek.
"""

import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agents.llm_provider import LLMClient
from agents.tinyfish_client import TinyFishClient
from agents.analysts import (
    FundamentalsAnalystAgent,
    TechnicalAnalystAgent,
    SentimentAnalystAgent,
    NewsMacroAnalystAgent,
)
from agents.researchers import BullishResearcherAgent, BearishResearcherAgent
from agents.execution import TraderAgent, RiskManagementAgent, PortfolioManagerAgent
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from packages.market_calendar.calendar import IST_TIMEZONE

logger = logging.getLogger("market_ai.hermes")


class HermesSupervisorBrain:
    """The central Hermes AI Brain supervising and orchestrating all specialized agents."""

    def __init__(self, model_name: Optional[str] = None):
        self.llm = LLMClient(provider="openrouter", model=model_name)
        self.tinyfish = TinyFishClient()
        self.market_provider = DevelopmentMarketDataProvider()

        # Specialized Agent Team
        self.fundamentals_analyst = FundamentalsAnalystAgent(self.llm)
        self.technical_analyst = TechnicalAnalystAgent(self.llm)
        self.sentiment_analyst = SentimentAnalystAgent(self.llm)
        self.news_macro_analyst = NewsMacroAnalystAgent(self.llm)
        self.bull_researcher = BullishResearcherAgent(self.llm)
        self.bear_researcher = BearishResearcherAgent(self.llm)
        self.trader = TraderAgent(self.llm)
        self.risk_manager = RiskManagementAgent(self.llm)
        self.portfolio_manager = PortfolioManagerAgent(self.llm)

    async def execute_supervisory_workflow(
        self,
        symbol: str,
        conduct_web_research: bool = True,
        portfolio_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Hermes Brain Execution Pipeline:
        1. Fetch Live Numerical Market Data (Source of Truth)
        2. Perform TinyFish Live Web/News Research
        3. Dispatch Parallel Analyst Subagents
        4. Moderate Researcher Debate (Bull vs Bear)
        5. Formulate Trade Order -> Audit Risk -> Authorize Execution
        6. Hermes Executive Synthesis
        """
        symbol = symbol.upper().strip()
        started_at = datetime.now(IST_TIMEZONE)

        # 1. Deterministic Market Data
        quote = await self.market_provider.get_quote(symbol)
        candles = await self.market_provider.get_history(symbol, timeframe="1D", limit=30)
        quote_data = quote.model_dump()

        # 2. TinyFish Web Research
        web_research: List[Dict[str, Any]] = []
        if conduct_web_research:
            query = f"{symbol} NSE India stock news quarterly results earnings"
            web_research = await self.tinyfish.search(query, limit=3)

        # 3. Parallel Analyst Subagents
        fund_task = self.fundamentals_analyst.analyze(symbol, quote_data)
        tech_task = self.technical_analyst.analyze(symbol, quote_data, candles)
        sent_task = self.sentiment_analyst.analyze(symbol)
        macro_task = self.news_macro_analyst.analyze(symbol)

        fund_rep, tech_rep, sent_rep, macro_rep = await asyncio.gather(
            fund_task, tech_task, sent_task, macro_task
        )

        analyst_reports = {
            "fundamentals": fund_rep,
            "technicals": tech_rep,
            "sentiment": sent_rep,
            "macro": macro_rep,
        }

        # 4. Research Debate (Bull vs Bear)
        bull_task = self.bull_researcher.argue(symbol, analyst_reports)
        bear_task = self.bear_researcher.argue(symbol, analyst_reports)
        bull_case, bear_case = await asyncio.gather(bull_task, bear_task)

        # 5. Lead Trader Formulation
        trade_proposal = await self.trader.decide_trade(
            symbol=symbol,
            current_price=quote.last_price,
            analyst_reports=analyst_reports,
            bull_case=bull_case,
            bear_case=bear_case,
        )

        # 6. Risk Manager Audit
        portfolio_state = portfolio_state or {"cash": 1_000_000.0, "total_value": 1_000_000.0, "positions": []}
        risk_evaluation = await self.risk_manager.evaluate_risk(
            symbol=symbol,
            trade_proposal=trade_proposal,
            portfolio_value=portfolio_state["total_value"],
        )

        # 7. Portfolio Manager Execution
        portfolio_decision = await self.portfolio_manager.authorize_trade(
            symbol=symbol,
            trader_proposal=trade_proposal,
            risk_evaluation=risk_evaluation,
            current_portfolio=portfolio_state,
        )

        # 8. Hermes Executive Synthesis
        system_prompt = (
            "You are Hermes, the Chief Autonomous Orchestration Intelligence of Market AI. "
            "Deliver an executive briefing synthesizing market data, live web intelligence, "
            "subagent debate results, and the finalized risk-adjusted trade execution."
        )

        user_prompt = (
            f"Hermes Executive Synthesis for {symbol}:\n"
            f"- Price: ₹{quote.last_price:,.2f} ({quote.percent_change:+.2f}%)\n"
            f"- TinyFish Web Research Findings: {[r.get('title') for r in web_research]}\n"
            f"- Bull Case: {bull_case.get('thesis')}\n"
            f"- Bear Case: {bear_case.get('thesis')}\n"
            f"- Final Trade: {trade_proposal.get('action')} {risk_evaluation.get('max_approved_shares')} shares @ ₹{trade_proposal.get('entry_price')}\n"
            f"- Target: ₹{trade_proposal.get('target_1')} | Stop: ₹{trade_proposal.get('stop_loss')} | R:R: {trade_proposal.get('risk_reward_ratio')}\n\n"
            "Provide a high-level executive summary for the investment committee."
        )

        hermes_briefing = await self.llm.generate(system_prompt, user_prompt)

        return {
            "supervisor": "Hermes Brain v3.0",
            "symbol": symbol,
            "execution_timestamp": started_at.isoformat(),
            "quote": quote_data,
            "web_research": web_research,
            "analyst_reports": analyst_reports,
            "debate": {
                "bull_case": bull_case,
                "bear_case": bear_case,
            },
            "trade_proposal": trade_proposal,
            "risk_evaluation": risk_evaluation,
            "portfolio_decision": portfolio_decision,
            "hermes_executive_briefing": hermes_briefing,
        }


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Supervisor Brain — Autonomous Investment Committee")
    parser.add_argument("--symbol", "-s", type=str, default="RELIANCE", help="Target Indian Stock (e.g. RELIANCE, TCS, HDFCBANK)")
    parser.add_argument("--research", "-r", action="store_true", default=True, help="Enable TinyFish live web research")
    parser.add_argument("--model", "-m", type=str, default="nousresearch/hermes-3-llama-3.1-70b", help="Hermes LLM model")
    args = parser.parse_args()

    print("\n\033[1m\033[96m================================================================================")
    print("                 HERMES SUPERVISOR BRAIN — ACTIVE REASONING")
    print("================================================================================\033[0m")
    print(f"[*] Target Asset: \033[1m{args.symbol.upper()}\033[0m")
    print(f"[*] TinyFish Web Intelligence: \033[92mCONNECTED\033[0m")
    print(f"[*] Hermes Model: \033[93m{args.model}\033[0m\n")

    brain = HermesSupervisorBrain(model_name=args.model)
    result = await brain.execute_supervisory_workflow(args.symbol, conduct_web_research=args.research)

    quote = result["quote"]
    trade = result["trade_proposal"]
    risk = result["risk_evaluation"]
    pm = result["portfolio_decision"]

    print(f"\033[92m[✓] Live Market Price:\033[0m \033[1m₹{quote['last_price']:,.2f}\033[0m ({quote['percent_change']:+.2f}%)")
    print(f"\033[96m[✓] TinyFish Research Results:\033[0m {len(result['web_research'])} news & filings extracted.")
    for idx, r in enumerate(result['web_research'], 1):
        print(f"    [{idx}] {r.get('title')} ({r.get('source', 'Web')})")

    print(f"\n\033[95m\033[1m>>> HERMES EXECUTIVE SYNTHESIS <<<\033[0m")
    print(f"{result['hermes_executive_briefing']}\n")

    print(f"\033[93m\033[1m>>> FINAL PORTFOLIO ACTION <<<\033[0m")
    print(f"• Action: \033[1m\033[92m{trade['action']} {risk['max_approved_shares']} shares\033[0m @ ₹{trade['entry_price']:,.2f}")
    print(f"• Target 1: ₹{trade['target_1']:,.2f} | Stop Loss: ₹{trade['stop_loss']:,.2f} (R:R: {trade['risk_reward_ratio']})")
    print(f"• Allocation: ₹{risk['capital_allocated_inr']:,.2f} (Portfolio Cash Left: ₹{pm['portfolio_impact']['new_cash']:,.2f})")
    print(f"• Status: \033[92m{pm['status']}\033[0m\n")
    print("\033[96m================================================================================\033[0m\n")


if __name__ == "__main__":
    asyncio.run(main())

"""
Market AI — Hermes Supervisor Brain (TradingAgents Orchestration Architecture)
Orchestrates 4 Concurrent Analysts, Bull/Bear Debate, Lead Trader, 3-Way Risk Committee, Reflection Memory, and Dossier Reporting.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
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
from agents.risk_mgmt import AggressiveRiskDebator, ConservativeRiskDebator, NeutralRiskArbiter
from agents.reflection import Reflector
from agents.reporting import write_report_tree
from agents.indicators import atr as compute_atr, detect_regime
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from packages.market_calendar.calendar import IST_TIMEZONE


class HermesSupervisorBrain:
    """Chief Executive & Supervisor moderating the 5-stage Trading Firm decision hierarchy."""

    def __init__(self):
        self.llm = LLMClient()
        self.tinyfish = TinyFishClient()
        self.market_provider = DevelopmentMarketDataProvider()

        # Stage 1: Analysts
        self.fundamentals_agent = FundamentalsAnalystAgent(self.llm)
        self.technical_agent = TechnicalAnalystAgent(self.llm)
        self.sentiment_agent = SentimentAnalystAgent(self.llm)
        self.macro_agent = NewsMacroAnalystAgent(self.llm)

        # Stage 2: Researchers
        self.bullish_researcher = BullishResearcherAgent(self.llm)
        self.bearish_researcher = BearishResearcherAgent(self.llm)

        # Stage 3: Lead Trader
        self.trader = TraderAgent(self.llm)

        # Stage 4: Risk Governance & 3-Way Risk Committee
        self.risk_manager = RiskManagementAgent(self.llm)
        self.aggressive_debator = AggressiveRiskDebator(self.llm)
        self.conservative_debator = ConservativeRiskDebator(self.llm)
        self.neutral_arbiter = NeutralRiskArbiter(self.llm)

        # Stage 5: Portfolio Manager & Reflection
        self.portfolio_manager = PortfolioManagerAgent(self.llm)
        self.reflector = Reflector(self.llm)

    async def execute_supervisory_workflow(
        self,
        symbol: str = "RELIANCE",
        portfolio_value: float = 1_000_000.0,
        conduct_web_research: bool = True,
        benchmark_symbol: str = "NIFTY",
    ) -> Dict[str, Any]:
        symbol_upper = symbol.upper().strip()
        quote = await self.market_provider.get_quote(symbol_upper)
        candles = await self.market_provider.get_history(symbol_upper, limit=240)
        try:
            bench_candles = await self.market_provider.get_history(benchmark_symbol, limit=120)
        except Exception:
            bench_candles = []
        quote_data = quote.model_dump()

        # Step 0: Inject Past Reflection Lessons from Memory Bank
        past_reflections = Reflector.get_recent_reflections(symbol_upper, limit=2)
        symbol_win_prob = Reflector.get_win_prob(symbol_upper)
        regime = detect_regime(candles)
        symbol_atr = compute_atr(candles, 14)

        # Step 1: TinyFish Web Intelligence
        web_intel = []
        if conduct_web_research:
            try:
                web_intel = await self.tinyfish.search(f"{symbol_upper} NSE India earnings results management", limit=2)
            except Exception:
                web_intel = [{"title": "Standard Trading Session", "snippet": "Market trading within normal bounds."}]

        # Step 2: Concurrent 4-Analyst Execution (all take candles now)
        fund_task = self.fundamentals_agent.analyze(symbol_upper, quote_data, candles)
        tech_task = self.technical_agent.analyze(symbol_upper, quote_data, candles)
        sent_task = self.sentiment_agent.analyze(symbol_upper, quote_data, candles)
        macro_task = self.macro_agent.analyze(symbol_upper, bench_candles)

        fund_rep, tech_rep, sent_rep, macro_rep = await asyncio.gather(
            fund_task, tech_task, sent_task, macro_task
        )

        analyst_reports = {
            "fundamentals": fund_rep,
            "technicals": tech_rep,
            "sentiment": sent_rep,
            "macro": macro_rep,
        }

        # Step 3: Dialectical Bull vs Bear Debate
        bull_task = self.bullish_researcher.argue(symbol_upper, analyst_reports)
        bear_task = self.bearish_researcher.argue(symbol_upper, analyst_reports)
        bull_case, bear_case = await asyncio.gather(bull_task, bear_task)

        # Step 4: Lead Trader Order Formulation (ATR-sized, direction from signals)
        trade_proposal = await self.trader.decide_trade(
            symbol=symbol_upper,
            current_price=quote.last_price,
            analyst_reports=analyst_reports,
            bull_case=bull_case,
            bear_case=bear_case,
            atr=symbol_atr,
        )

        # Step 5: 3-Way Risk Committee Debate (regime-aware, learned win_prob)
        agg_task = self.aggressive_debator.argue(symbol_upper, trade_proposal, market_regime=regime)
        cons_task = self.conservative_debator.argue(symbol_upper, trade_proposal, market_regime=regime)
        agg_case, cons_case = await asyncio.gather(agg_task, cons_task)

        risk_arbitration = await self.neutral_arbiter.arbitrate(
            symbol=symbol_upper,
            trade_proposal=trade_proposal,
            aggressive_case=agg_case,
            conservative_case=cons_case,
            india_vix=14.5,
            win_prob=symbol_win_prob,
        )

        # Step 6: Risk Manager & Portfolio Clearance
        risk_eval = await self.risk_manager.evaluate_risk(
            symbol=symbol_upper,
            trade_proposal=trade_proposal,
            portfolio_value=portfolio_value,
        )

        current_portfolio = {
            "cash": portfolio_value,
            "total_value": portfolio_value,
            "positions": [],
        }
        pm_decision = await self.portfolio_manager.authorize_trade(
            symbol=symbol_upper,
            trader_proposal=trade_proposal,
            risk_evaluation=risk_eval,
            current_portfolio=current_portfolio,
        )

        # Step 7: Chief Supervisor Synthesis Memo
        supervisor_memo = await self._generate_supervisor_synthesis(
            symbol=symbol_upper,
            quote=quote_data,
            analyst_reports=analyst_reports,
            bull_case=bull_case,
            bear_case=bear_case,
            trade_proposal=trade_proposal,
            risk_arbitration=risk_arbitration,
            past_lessons=[r.get("lesson", "") for r in past_reflections],
        )

        state = {
            "supervisor": "Hermes Brain v4.0 (Signal-Driven)",
            "symbol": symbol_upper,
            "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
            "quote": quote_data,
            "regime": regime,
            "learned_win_prob": symbol_win_prob,
            "atr_14": symbol_atr,
            "past_reflections": past_reflections,
            "web_research": web_intel,
            "analyst_reports": analyst_reports,
            "debate": {
                "bull_case": bull_case,
                "bear_case": bear_case,
            },
            "trade_proposal": trade_proposal,
            "risk_committee": {
                "aggressive": agg_case,
                "conservative": cons_case,
                "neutral_arbitration": risk_arbitration,
            },
            "risk_evaluation": risk_eval,
            "portfolio_decision": pm_decision,
            "hermes_executive_briefing": supervisor_memo,
        }

        # Step 8: Write Hierarchical Report Tree
        try:
            dossier_path = write_report_tree(state, symbol_upper)
            state["dossier_file_path"] = str(dossier_path)
        except Exception:
            pass

        return state

    async def _generate_supervisor_synthesis(
        self,
        symbol: str,
        quote: Dict[str, Any],
        analyst_reports: Dict[str, Any],
        bull_case: Dict[str, Any],
        bear_case: Dict[str, Any],
        trade_proposal: Dict[str, Any],
        risk_arbitration: Dict[str, Any],
        past_lessons: List[str],
    ) -> str:
        system_prompt = (
            "You are Hermes, Chief Investment Supervisor at an institutional quantitative fund. "
            "Deliver an authoritative executive briefing memo synthesizing the 4 analyst reports, "
            "the dialectical Bull/Bear debate, the 3-way Risk Committee compromise, and historical lessons."
        )

        lessons_block = "\n".join(f"- Past Lesson: {l}" for l in past_lessons) if past_lessons else "No prior recorded lessons."

        user_prompt = (
            f"Synthesize trading committee memo for {symbol} (CMP: ₹{quote.get('last_price')}):\n"
            f"1. Key Analyst Insights (Fundamentals, Technicals, Sentiment, Macro)\n"
            f"2. Bull Thesis: {bull_case.get('thesis')}\n"
            f"3. Bear Thesis: {bear_case.get('thesis')}\n"
            f"4. Lead Trader Action: {trade_proposal.get('action')} @ ₹{trade_proposal.get('entry_price')} "
            f"(Target: ₹{trade_proposal.get('target_1')}, Stop: ₹{trade_proposal.get('stop_loss')})\n"
            f"5. Risk Committee Verdict: {risk_arbitration.get('consensus_summary')}\n"
            f"6. Memory Bank Insights:\n{lessons_block}\n\n"
            "Format with: [EXECUTIVE SUMMARY], [CORE CONVICTION], [RISK SAFEGUARDS], [FINAL VERDICT]."
        )

        # Executive memo: heaviest synthesis in the firm — send to LongCat for the deep pass.
        return await self.llm.generate(system_prompt, user_prompt, force=True, heavy=True)

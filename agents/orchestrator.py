"""
Market AI — Multi-Agent Trading Firm Orchestrator
Coordinates Analysts -> Researchers Debate -> Lead Trader -> Risk Manager -> Portfolio Manager.
"""

import asyncio
from typing import Dict, Any, Optional
from agents.llm_provider import LLMClient
from agents.analysts import (
    FundamentalsAnalystAgent,
    TechnicalAnalystAgent,
    SentimentAnalystAgent,
    NewsMacroAnalystAgent,
)
from agents.researchers import BullishResearcherAgent, BearishResearcherAgent
from agents.execution import TraderAgent, RiskManagementAgent, PortfolioManagerAgent
from agents.indicators import atr as compute_atr
from packages.market_data.development_provider import DevelopmentMarketDataProvider


class TradingFirmOrchestrator:
    """Coordinates the AI Trading Firm agent ecosystem."""

    def __init__(self, provider_name: Optional[str] = None):
        self.llm = LLMClient(provider=provider_name)
        self.market_provider = DevelopmentMarketDataProvider()

        # 1. Analyst Team
        self.fundamentals_analyst = FundamentalsAnalystAgent(self.llm)
        self.technical_analyst = TechnicalAnalystAgent(self.llm)
        self.sentiment_analyst = SentimentAnalystAgent(self.llm)
        self.news_macro_analyst = NewsMacroAnalystAgent(self.llm)

        # 2. Researcher Debate Team
        self.bull_researcher = BullishResearcherAgent(self.llm)
        self.bear_researcher = BearishResearcherAgent(self.llm)

        # 3. Execution & Governance Team
        self.trader = TraderAgent(self.llm)
        self.risk_manager = RiskManagementAgent(self.llm)
        self.portfolio_manager = PortfolioManagerAgent(self.llm)

    async def run_analysis_pipeline(
        self,
        symbol: str,
        portfolio_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Runs the complete trading firm workflow for a given symbol."""
        if portfolio_state is None:
            portfolio_state = {"cash": 1_000_000.0, "total_value": 1_000_000.0, "positions": []}

        # Step 1: Fetch real-time market quote and historical data
        quote = await self.market_provider.get_quote(symbol)
        candles = await self.market_provider.get_history(symbol, timeframe="1D", limit=240)
        try:
            bench = await self.market_provider.get_history("NIFTY", timeframe="1D", limit=120)
        except Exception:
            bench = []
        quote_dict = quote.model_dump()
        symbol_atr = compute_atr(candles, 14)

        # Step 2: Analyst Team Runs (in parallel, all fed real candles now)
        fund_task = self.fundamentals_analyst.analyze(symbol, quote_dict, candles)
        tech_task = self.technical_analyst.analyze(symbol, quote_dict, candles)
        sent_task = self.sentiment_analyst.analyze(symbol, quote_dict, candles)
        macro_task = self.news_macro_analyst.analyze(symbol, bench)

        fund_rep, tech_rep, sent_rep, macro_rep = await asyncio.gather(
            fund_task, tech_task, sent_task, macro_task
        )

        analyst_reports = {
            "fundamentals": fund_rep,
            "technicals": tech_rep,
            "sentiment": sent_rep,
            "macro": macro_rep,
        }

        # Step 3: Researcher Team Debate (Bull vs Bear)
        bull_task = self.bull_researcher.argue(symbol, analyst_reports)
        bear_task = self.bear_researcher.argue(symbol, analyst_reports)
        bull_case, bear_case = await asyncio.gather(bull_task, bear_task)

        # Step 4: Trader Agent Decision (ATR-sized, direction from signal aggregation)
        trade_proposal = await self.trader.decide_trade(
            symbol=symbol,
            current_price=quote.last_price,
            analyst_reports=analyst_reports,
            bull_case=bull_case,
            bear_case=bear_case,
            atr=symbol_atr,
        )

        # Step 5: Risk Manager Audit
        risk_evaluation = await self.risk_manager.evaluate_risk(
            symbol=symbol,
            trade_proposal=trade_proposal,
            portfolio_value=portfolio_state.get("total_value", 1_000_000.0),
        )

        # Step 6: Portfolio Manager Final Authorization
        portfolio_decision = await self.portfolio_manager.authorize_trade(
            symbol=symbol,
            trader_proposal=trade_proposal,
            risk_evaluation=risk_evaluation,
            current_portfolio=portfolio_state,
        )

        return {
            "symbol": symbol,
            "quote": quote_dict,
            "analyst_reports": analyst_reports,
            "debate": {
                "bull_case": bull_case,
                "bear_case": bear_case,
            },
            "trade_proposal": trade_proposal,
            "risk_evaluation": risk_evaluation,
            "portfolio_decision": portfolio_decision,
        }

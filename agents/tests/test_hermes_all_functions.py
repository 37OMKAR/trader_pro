"""
Comprehensive Test Suite for Hermes Supervisor Brain & LongCat / TinyFish Integration
Verifies all 9 specialized functions and end-to-end supervisory workflows.
"""

import pytest
from agents.llm_provider import LLMClient
from agents.tinyfish_client import TinyFishClient
from agents.hermes_brain import HermesSupervisorBrain
from agents.analysts import (
    FundamentalsAnalystAgent,
    TechnicalAnalystAgent,
    SentimentAnalystAgent,
    NewsMacroAnalystAgent,
)
from agents.researchers import BullishResearcherAgent, BearishResearcherAgent
from agents.execution import TraderAgent, RiskManagementAgent, PortfolioManagerAgent
from packages.market_data.development_provider import DevelopmentMarketDataProvider


@pytest.mark.anyio
async def test_llm_client_longcat_and_openrouter():
    """Test 1: LLM Client routing across LongCat, OpenRouter Hermes, and DeepSeek."""
    client = LLMClient()
    response = await client.generate(
        system_prompt="You are Hermes AI.",
        user_prompt="Say 'Hermes Online'",
    )
    assert response is not None
    assert len(response) > 0


@pytest.mark.anyio
async def test_tinyfish_search_and_fetch():
    """Test 2: TinyFish web search and live filings fetch."""
    tinyfish = TinyFishClient()
    results = await tinyfish.search("RELIANCE quarterly results", limit=2)
    assert isinstance(results, list)
    assert len(results) >= 1
    assert "title" in results[0]

    page = await tinyfish.fetch_page("https://www.nseindia.com")
    assert "content" in page


@pytest.mark.anyio
async def test_four_specialized_analysts():
    """Test 3: Parallel execution of 4 Specialized Analyst Agents."""
    llm = LLMClient()
    provider = DevelopmentMarketDataProvider()
    quote = await provider.get_quote("TCS")
    candles = await provider.get_history("TCS", limit=30)
    quote_data = quote.model_dump()

    fund_agent = FundamentalsAnalystAgent(llm)
    tech_agent = TechnicalAnalystAgent(llm)
    sent_agent = SentimentAnalystAgent(llm)
    macro_agent = NewsMacroAnalystAgent(llm)

    fund_rep = await fund_agent.analyze("TCS", quote_data)
    tech_rep = await tech_agent.analyze("TCS", quote_data, candles)
    sent_rep = await sent_agent.analyze("TCS")
    macro_rep = await macro_agent.analyze("TCS")

    assert ("summary" in fund_rep or "report" in fund_rep)
    assert ("summary" in tech_rep or "report" in tech_rep)
    assert ("summary" in sent_rep or "report" in sent_rep)
    assert ("summary" in macro_rep or "report" in macro_rep)


@pytest.mark.anyio
async def test_bull_vs_bear_debate_team():
    """Test 4: Bullish vs Bearish Researcher Debate Arena."""
    llm = LLMClient()
    bull_agent = BullishResearcherAgent(llm)
    bear_agent = BearishResearcherAgent(llm)

    mock_reports = {
        "fundamentals": {"summary": "High ROE and low debt."},
        "technicals": {"summary": "Golden DMA alignment."},
        "sentiment": {"summary": "Positive PCR at 1.25."},
        "macro": {"summary": "Steady Indian GDP growth."},
    }

    bull_case = await bull_agent.argue("INFY", mock_reports)
    bear_case = await bear_agent.argue("INFY", mock_reports)

    assert "thesis" in bull_case and len(bull_case.get("catalysts", [])) >= 1
    assert "thesis" in bear_case and len(bear_case.get("risk_triggers", [])) >= 1


@pytest.mark.anyio
async def test_trader_and_risk_governance():
    """Test 5: Lead Trader Formulation & Risk Manager Audit Clearance."""
    llm = LLMClient()
    trader = TraderAgent(llm)
    risk_manager = RiskManagementAgent(llm)
    pm = PortfolioManagerAgent(llm)

    trade_proposal = await trader.decide_trade(
        symbol="HDFCBANK",
        current_price=1650.0,
        analyst_reports={"fundamentals": {}, "technicals": {}, "sentiment": {}, "macro": {}},
        bull_case={"thesis": "Strong credit expansion.", "catalysts": []},
        bear_case={"thesis": "NIM compression risk.", "risks": []},
    )
    assert trade_proposal["action"] in ["BUY", "SELL", "HOLD"]
    assert trade_proposal["target_1"] > 0
    assert trade_proposal["stop_loss"] > 0

    risk_eval = await risk_manager.evaluate_risk(
        symbol="HDFCBANK",
        trade_proposal=trade_proposal,
        portfolio_value=1_000_000.0,
    )
    assert risk_eval["status"] in ["APPROVED", "ADJUSTED"]
    assert risk_eval["max_approved_shares"] > 0

    pm_res = await pm.authorize_trade(
        symbol="HDFCBANK",
        trader_proposal=trade_proposal,
        risk_evaluation=risk_eval,
        current_portfolio={"cash": 1_000_000.0, "total_value": 1_000_000.0, "positions": []},
    )
    assert pm_res["status"] == "EXECUTED_IN_PAPER_PORTFOLIO"


@pytest.mark.anyio
async def test_hermes_end_to_end_supervisory_workflow():
    """Test 6: Full Hermes Supervisor Brain end-to-end workflow."""
    brain = HermesSupervisorBrain()
    res = await brain.execute_supervisory_workflow("RELIANCE", conduct_web_research=True)

    assert res["supervisor"] == "Hermes Brain v3.0"
    assert res["symbol"] == "RELIANCE"
    assert "web_research" in res
    assert "analyst_reports" in res
    assert "debate" in res
    assert "trade_proposal" in res
    assert "risk_evaluation" in res
    assert "portfolio_decision" in res
    assert "hermes_executive_briefing" in res
    assert len(res["hermes_executive_briefing"]) > 0

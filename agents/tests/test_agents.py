"""
Unit tests for the Multi-Agent Trading Firm framework.
"""

import pytest
from agents.orchestrator import TradingFirmOrchestrator
from agents.llm_provider import LLMClient


@pytest.mark.anyio
async def test_llm_client_fallback():
    client = LLMClient(provider="mock")
    response = await client.generate("system prompt", "user prompt")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.anyio
async def test_trading_firm_orchestrator_pipeline():
    orchestrator = TradingFirmOrchestrator(provider_name="mock")
    result = await orchestrator.run_analysis_pipeline("INFY")

    # 1. Verification of Symbol & Quote
    assert result["symbol"] == "INFY"
    assert result["quote"]["last_price"] > 0

    # 2. Verification of Analyst Reports
    analysts = result["analyst_reports"]
    assert "fundamentals" in analysts
    assert "technicals" in analysts
    assert "sentiment" in analysts
    assert "macro" in analysts
    assert analysts["fundamentals"]["metrics"]["roe_pct"] > 0

    # 3. Verification of Debate Team
    debate = result["debate"]
    assert debate["bull_case"]["stance"] == "BULLISH"
    assert debate["bear_case"]["stance"] == "BEARISH"
    assert len(debate["bull_case"]["catalysts"]) >= 3
    assert len(debate["bear_case"]["risk_triggers"]) >= 3

    # 4. Verification of Trader & Risk Manager
    trade = result["trade_proposal"]
    assert trade["action"] in ["BUY", "SELL", "HOLD"]
    assert trade["entry_price"] > 0
    assert trade["stop_loss"] < trade["entry_price"]
    assert trade["target_1"] > trade["entry_price"]

    risk = result["risk_evaluation"]
    assert risk["approved"] is True
    assert risk["max_approved_shares"] > 0

    # 5. Verification of Portfolio Manager Execution
    pm = result["portfolio_decision"]
    assert pm["status"] == "EXECUTED_IN_PAPER_PORTFOLIO"
    assert pm["trade_executed"] is True
    assert pm["order_details"]["quantity"] > 0

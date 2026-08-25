"""
Unit tests for TradingAgents Enrichments (3-Way Risk Committee, Reflection Memory, and Report Tree).
"""

import pytest
from pathlib import Path
from agents.llm_provider import LLMClient
from agents.risk_mgmt import AggressiveRiskDebator, ConservativeRiskDebator, NeutralRiskArbiter
from agents.reflection import Reflector
from agents.reporting import write_report_tree
from agents.hermes_brain import HermesSupervisorBrain


@pytest.mark.anyio
async def test_three_way_risk_committee_debate():
    llm = LLMClient()
    agg = AggressiveRiskDebator(llm)
    cons = ConservativeRiskDebator(llm)
    arb = NeutralRiskArbiter(llm)

    mock_trade = {
        "action": "BUY",
        "entry_price": 2500.0,
        "target_1": 2650.0,
        "stop_loss": 2420.0,
        "suggested_allocation_pct": 12.0,
    }

    agg_case = await agg.argue("RELIANCE", mock_trade, market_regime="BULL")
    cons_case = await cons.argue("RELIANCE", mock_trade, market_regime="BULL")

    assert agg_case["recommended_allocation_pct"] > cons_case["recommended_allocation_pct"]
    assert "argument" in agg_case
    assert "argument" in cons_case

    arbitration = await arb.arbitrate(
        symbol="RELIANCE",
        trade_proposal=mock_trade,
        aggressive_case=agg_case,
        conservative_case=cons_case,
        india_vix=15.0,
        win_prob=0.60,
    )

    assert arbitration["verdict"] == "CONSENSUS_APPROVED"
    assert arbitration["approved_allocation_pct"] > 0
    assert "kelly_fraction" in arbitration


@pytest.mark.anyio
async def test_post_trade_reflection_and_memory():
    llm = LLMClient()
    reflector = Reflector(llm)

    entry = await reflector.reflect_on_trade(
        symbol="TATAMOTORS",
        initial_thesis="Breakout above 1000 with auto sector tailwind.",
        raw_return_pct=5.5,
        alpha_vs_nifty_pct=3.8,
        exit_reason="TARGET_HIT",
    )

    assert entry["symbol"] == "TATAMOTORS"
    assert entry["alpha_vs_nifty_pct"] == 3.8
    assert len(entry["lesson"]) > 0

    recent = Reflector.get_recent_reflections("TATAMOTORS")
    assert len(recent) >= 1
    assert recent[-1]["symbol"] == "TATAMOTORS"


@pytest.mark.anyio
async def test_hierarchical_report_tree_writing(tmp_path):
    mock_state = {
        "quote": {"last_price": 2500.0},
        "analyst_reports": {
            "fundamentals": {"summary": "Low debt, high ROE."},
            "technicals": {"summary": "20 DMA above 50 DMA."},
        },
        "debate": {
            "bull_case": {"thesis": "Earnings growth.", "catalysts": ["New product launch"]},
            "bear_case": {"thesis": "Valuation premium.", "risk_triggers": ["Margin squeeze"]},
        },
        "trade_proposal": {
            "action": "BUY",
            "entry_price": 2500.0,
            "target_1": 2650.0,
            "stop_loss": 2420.0,
            "risk_reward_ratio": "1:1.9",
            "suggested_allocation_pct": 10.0,
            "rationale": "High conviction breakout.",
        },
        "risk_evaluation": {
            "status": "APPROVED",
            "max_approved_shares": 40,
            "capital_allocated_inr": 100000.0,
            "max_drawdown_risk_inr": 3200.0,
            "risk_of_portfolio_pct": 0.32,
            "summary": "Risk within tolerance.",
        },
        "hermes_executive_briefing": "Executive Summary: Buy approved.",
    }

    report_path = write_report_tree(mock_state, "RELIANCE", save_path=str(tmp_path))
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Institutional Research & Trading Dossier" in content
    assert "Specialized Analyst Team Reports" in content

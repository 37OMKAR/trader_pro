"""
Market AI — Institutional Research Dossier & Report Tree Writer
Adapted from TradingAgents reporting framework for comprehensive multi-section trading intelligence export.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def write_report_tree(deliberation_state: Dict[str, Any], symbol: str, save_path: str = "artifacts/reports") -> Path:
    """Saves completed deliberation into structured markdown dossier and returns complete_report.md path."""
    out_dir = Path(save_path) / symbol.upper()
    out_dir.mkdir(parents=True, exist_ok=True)
    sections = []

    quote = deliberation_state.get("quote", {})
    reports = deliberation_state.get("analyst_reports", {})
    debate = deliberation_state.get("debate", {})
    trade = deliberation_state.get("trade_proposal", {})
    risk = deliberation_state.get("risk_evaluation", {})
    pm = deliberation_state.get("portfolio_decision", {})
    briefing = deliberation_state.get("hermes_executive_briefing", "")

    # 1. Analyst Team Reports
    analysts_dir = out_dir / "1_analysts"
    analysts_dir.mkdir(exist_ok=True)
    analyst_blocks = []

    if "fundamentals" in reports:
        txt = reports["fundamentals"].get("summary", "") + "\n\n" + reports["fundamentals"].get("llm_commentary", "")
        (analysts_dir / "fundamentals.md").write_text(txt, encoding="utf-8")
        analyst_blocks.append(f"### Fundamentals Analyst\n{txt}")

    if "technicals" in reports:
        txt = reports["technicals"].get("summary", "") + "\n\n" + reports["technicals"].get("llm_commentary", "")
        (analysts_dir / "technicals.md").write_text(txt, encoding="utf-8")
        analyst_blocks.append(f"### Technical Pattern Analyst\n{txt}")

    if "sentiment" in reports:
        txt = reports["sentiment"].get("summary", "") + "\n\n" + reports["sentiment"].get("llm_commentary", "")
        (analysts_dir / "sentiment.md").write_text(txt, encoding="utf-8")
        analyst_blocks.append(f"### Sentiment & Derivatives Analyst\n{txt}")

    if "macro" in reports:
        txt = reports["macro"].get("summary", "") + "\n\n" + reports["macro"].get("llm_commentary", "")
        (analysts_dir / "macro.md").write_text(txt, encoding="utf-8")
        analyst_blocks.append(f"### Macroeconomic & Policy Analyst\n{txt}")

    if analyst_blocks:
        sections.append("## I. Specialized Analyst Team Reports\n\n" + "\n\n".join(analyst_blocks))

    # 2. Research Team Debate
    if debate:
        research_dir = out_dir / "2_research"
        research_dir.mkdir(exist_ok=True)
        bull_txt = f"**Bullish Thesis**: {debate.get('bull_case', {}).get('thesis', '')}\n\n**Catalysts**:\n" + "\n".join(f"- {c}" for c in debate.get('bull_case', {}).get('catalysts', []))
        bear_txt = f"**Bearish Thesis**: {debate.get('bear_case', {}).get('thesis', '')}\n\n**Risk Triggers**:\n" + "\n".join(f"- {r}" for r in debate.get('bear_case', {}).get('risk_triggers', []))
        
        (research_dir / "bull_case.md").write_text(bull_txt, encoding="utf-8")
        (research_dir / "bear_case.md").write_text(bear_txt, encoding="utf-8")
        sections.append(f"## II. Research Team Dialectical Debate\n\n### Bull Case\n{bull_txt}\n\n### Bear Case\n{bear_txt}")

    # 3. Trading Team Execution Plan
    if trade:
        trading_dir = out_dir / "3_trading"
        trading_dir.mkdir(exist_ok=True)
        trade_txt = (
            f"- **Action**: {trade.get('action')}\n"
            f"- **Entry Price**: ₹{trade.get('entry_price')}\n"
            f"- **Target 1**: ₹{trade.get('target_1')}\n"
            f"- **Stop Loss**: ₹{trade.get('stop_loss')}\n"
            f"- **Risk/Reward Ratio**: {trade.get('risk_reward_ratio')}\n"
            f"- **Suggested Allocation**: {trade.get('suggested_allocation_pct')}%\n\n"
            f"**Rational Strategy**: {trade.get('rationale')}"
        )
        (trading_dir / "execution_plan.md").write_text(trade_txt, encoding="utf-8")
        sections.append(f"## III. Lead Trader Execution Formulation\n\n{trade_txt}")

    # 4. Risk Management Committee
    if risk:
        risk_dir = out_dir / "4_risk"
        risk_dir.mkdir(exist_ok=True)
        risk_txt = (
            f"- **Risk Verdict**: {risk.get('status')}\n"
            f"- **Max Approved Shares**: {risk.get('max_approved_shares')}\n"
            f"- **Allocated Capital**: ₹{risk.get('capital_allocated_inr'):,.2f}\n"
            f"- **Max Portfolio Risk**: ₹{risk.get('max_drawdown_risk_inr'):,.2f} ({risk.get('risk_of_portfolio_pct')}%)\n\n"
            f"**CRO Governance Audit**: {risk.get('summary')}"
        )
        (risk_dir / "risk_audit.md").write_text(risk_txt, encoding="utf-8")
        sections.append(f"## IV. Risk Management Committee Audit\n\n{risk_txt}")

    # 5. Chief Supervisor Synthesis
    if briefing:
        portfolio_dir = out_dir / "5_portfolio"
        portfolio_dir.mkdir(exist_ok=True)
        (portfolio_dir / "hermes_memo.md").write_text(briefing, encoding="utf-8")
        sections.append(f"## V. Hermes Chief Supervisor Synthesis Memo\n\n{briefing}")

    # Consolidated complete report
    header = (
        f"# Institutional Research & Trading Dossier: {symbol.upper()}\n\n"
        f"- **Generated At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n"
        f"- **Market Price**: ₹{quote.get('last_price', 'N/A')}\n"
        f"- **Platform**: Market AI / Hermes Brain v3.0\n\n"
        f"---\n\n"
    )
    complete_report_path = out_dir / "complete_report.md"
    complete_report_path.write_text(header + "\n\n---\n\n".join(sections), encoding="utf-8")

    return complete_report_path

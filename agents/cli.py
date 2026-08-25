"""
Market AI — Trading Firm Command Line Interface (CLI)
Interactive CLI runner for the multi-agent trading firm.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import argparse
from typing import Optional
from dotenv import load_dotenv

# Ensure UTF-8 output encoding across all terminals (including Windows cp1252)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load .env variables
load_dotenv()

from agents.orchestrator import TradingFirmOrchestrator
from packages.market_data.development_provider import INDIAN_EQUITY_UNIVERSE

# ANSI Terminal Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    banner = f"""
{CYAN}{BOLD}================================================================================
          MARKET AI — AUTONOMOUS MULTI-AGENT TRADING FIRM (INDIA)
================================================================================{RESET}
{DIM}  Specialized Agents: Fundamentals | Technicals | Sentiment | Macro
  Debate Team:        Bullish Researcher vs Bearish Researcher
  Governance:         Lead Trader -> Risk Manager -> Portfolio Manager{RESET}
--------------------------------------------------------------------------------
"""
    print(banner)


async def run_cli(symbol: str, llm_provider: Optional[str] = None):
    print_banner()
    symbol = symbol.upper().strip()
    print(f"{YELLOW}[+] Initializing Trading Firm for target asset:{RESET} {BOLD}{symbol}{RESET}", flush=True)
    print(f"{DIM}[*] Active LLM Engine:{RESET} {CYAN}{llm_provider or 'Hermes-3 70B / DeepSeek-V3 Quant Synthesizer'}{RESET}\n", flush=True)

    orchestrator = TradingFirmOrchestrator(provider_name=llm_provider)

    # 1. Analysts
    print(f"{BOLD}{CYAN}>>> PHASE 1: SPECIALIZED ANALYST REPORTS <<<{RESET}", flush=True)
    print(f"{DIM}[1/4] Running Fundamentals Analyst...{RESET}", flush=True)
    print(f"{DIM}[2/4] Running Technical Pattern Analyst...{RESET}", flush=True)
    print(f"{DIM}[3/4] Running Sentiment & PCR Derivatives Analyst...{RESET}", flush=True)
    print(f"{DIM}[4/4] Running Macroeconomic & RBI Policy Analyst...{RESET}", flush=True)

    result = await orchestrator.run_analysis_pipeline(symbol)

    quote = result["quote"]
    analysts = result["analyst_reports"]
    debate = result["debate"]
    trade = result["trade_proposal"]
    risk = result["risk_evaluation"]
    pm = result["portfolio_decision"]

    print(f"\n{GREEN}[✓] Current Market Price:{RESET} {BOLD}₹{quote['last_price']:,.2f}{RESET} ({quote['percent_change']:+.2f}%)\n")

    print(f"  {BOLD}• Fundamentals:{RESET} {analysts['fundamentals']['summary']}")
    print(f"  {BOLD}• Technicals:{RESET}   {analysts['technicals']['summary']}")
    print(f"  {BOLD}• Sentiment:{RESET}    {analysts['sentiment']['summary']}")
    print(f"  {BOLD}• Macro:{RESET}        {analysts['macro']['summary']}\n")

    # 2. Debate
    print(f"{BOLD}{MAGENTA}>>> PHASE 2: RESEARCH TEAM DEBATE (BULL VS BEAR) <<<{RESET}")
    print(f"  {GREEN}{BOLD}[BULL CASE]{RESET} {debate['bull_case']['thesis']}")
    for cat in debate['bull_case']['catalysts']:
        print(f"    + {cat}")
    print()
    print(f"  {RED}{BOLD}[BEAR CASE]{RESET} {debate['bear_case']['thesis']}")
    for trig in debate['bear_case']['risk_triggers']:
        print(f"    - {trig}")
    print()

    # 3. Trader
    print(f"{BOLD}{YELLOW}>>> PHASE 3: LEAD TRADER ACTION PROPOSAL <<<{RESET}")
    print(f"  {BOLD}Action:{RESET}            {GREEN if trade['action'] == 'BUY' else RED}{BOLD}{trade['action']}{RESET}")
    print(f"  {BOLD}Entry Price:{RESET}       ₹{trade['entry_price']:,.2f}")
    print(f"  {BOLD}Stop Loss:{RESET}         ₹{trade['stop_loss']:,.2f} ({DIM}Protective Exit{RESET})")
    print(f"  {BOLD}Target 1:{RESET}          ₹{trade['target_1']:,.2f} ({GREEN}+7.0%{RESET})")
    print(f"  {BOLD}Target 2:{RESET}          ₹{trade['target_2']:,.2f} ({GREEN}+12.0%{RESET})")
    print(f"  {BOLD}Risk/Reward:{RESET}       {trade['risk_reward_ratio']}")
    print(f"  {BOLD}Rationale:{RESET}         {trade['rationale']}\n")

    # 4. Risk Manager
    print(f"{BOLD}{CYAN}>>> PHASE 4: RISK MANAGEMENT GOVERNANCE <<<{RESET}")
    print(f"  {BOLD}Verdict:{RESET}           {GREEN if risk['approved'] else RED}{risk['status']}{RESET}")
    print(f"  {BOLD}Position Limit:{RESET}    {risk['max_approved_shares']} shares (₹{risk['capital_allocated_inr']:,.2f})")
    print(f"  {BOLD}Max Rupee Risk:{RESET}    ₹{risk['max_drawdown_risk_inr']:,.2f} ({risk['risk_of_portfolio_pct']}% of total capital)")
    print(f"  {BOLD}Risk Clearance:{RESET}    {risk['summary']}\n")

    # 5. Portfolio Manager
    print(f"{BOLD}{GREEN}>>> PHASE 5: PORTFOLIO MANAGER AUTHORIZATION & EXECUTION <<<{RESET}")
    print(f"  {BOLD}Status:{RESET}            {GREEN}{BOLD}{pm['status']}{RESET}")
    print(f"  {BOLD}Order Summary:{RESET}     {pm['executive_memo']}")
    print(f"  {BOLD}Portfolio Cash:{RESET}    ₹{pm['portfolio_impact']['new_cash']:,.2f} ({pm['portfolio_impact']['allocated_percentage']}% allocated)\n")
    print(f"{CYAN}================================================================================{RESET}")
    print(f"{GREEN}[✓] Trading cycle complete. Trade recorded in simulated paper portfolio.{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Market AI — Autonomous Multi-Agent Trading Firm CLI")
    parser.add_argument(
        "--symbol",
        "-s",
        type=str,
        default="RELIANCE",
        help="Indian stock symbol (e.g. RELIANCE, TCS, HDFCBANK, INFY, TATAMOTORS)",
    )
    parser.add_argument(
        "--llm",
        "-l",
        type=str,
        choices=["gemini", "openai", "claude", "mock"],
        default=None,
        help="LLM provider backend (gemini, openai, claude, mock)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Launch interactive stock selector",
    )

    args = parser.parse_args()

    if args.interactive:
        print_banner()
        print(f"{BOLD}Available Indian Equities Universe:{RESET}")
        for idx, stock in enumerate(INDIAN_EQUITY_UNIVERSE[:10], 1):
            print(f"  [{idx}] {stock['symbol']} — {stock['name']} ({stock['sector']})")
        print("  ...")
        try:
            choice = input(f"\n{BOLD}Enter symbol name (or number 1-10): {RESET}").strip().upper()
            if choice.isdigit() and 1 <= int(choice) <= 10:
                symbol = INDIAN_EQUITY_UNIVERSE[int(choice) - 1]["symbol"]
            else:
                symbol = choice or "RELIANCE"
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)
    else:
        symbol = args.symbol

    asyncio.run(run_cli(symbol, args.llm))


if __name__ == "__main__":
    main()

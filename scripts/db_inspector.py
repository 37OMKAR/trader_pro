import sqlite3
import json

conn = sqlite3.connect("market_ai.db")
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("DATABASE TABLES IN market_ai.db:")
for t in tables:
    name = t[0]
    count = cursor.execute(f"SELECT COUNT(*) FROM {name};").fetchone()[0]
    print(f" - {name:<26}: {count} records")

print("\nSAMPLE AGENT DELIBERATIONS:")
delibs = cursor.execute("SELECT deliberation_id, symbol, market_regime, status, created_at FROM agent_deliberations LIMIT 5;").fetchall()
for d in delibs:
    print("  *", d)

print("\nSAMPLE STRATEGIES & BACKTESTS:")
strats = cursor.execute("SELECT strategy_id, name, version, status FROM strategies LIMIT 5;").fetchall()
for s in strats:
    print("  *", s)

print("\nPAPER ACCOUNTS & TRADES:")
accs = cursor.execute("SELECT account_id, name, current_cash, portfolio_value FROM paper_accounts LIMIT 3;").fetchall()
for a in accs:
    print("  *", a)

trades = cursor.execute("SELECT trade_id, symbol, side, quantity, price, amount FROM paper_trades LIMIT 5;").fetchall()
for tr in trades:
    print("  *", tr)

print("\nTOURNAMENT LEADERBOARD:")
leaders = cursor.execute("SELECT rank, name, strategy_score, badge FROM tournament_leaderboard LIMIT 5;").fetchall()
for l in leaders:
    print("  *", l)

print("\nPOST-TRADE REFLECTION MEMORY:")
refls = cursor.execute("SELECT symbol, action, alpha_vs_nifty, lesson_learned FROM reflection_memory LIMIT 3;").fetchall()
for r in refls:
    print(f"  * {r[0]} ({r[1]}): Alpha vs NIFTY {r[2]:+.2f}% | Lesson: {r[3][:80]}...")

conn.close()

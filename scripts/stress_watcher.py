"""
Emits one JSON line every N seconds summarizing firm state.
Runs alongside apps.autonomous.scheduler during a soak run.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone, timedelta
from ops import state as ops_state

IST = timezone(timedelta(hours=5, minutes=30))

def snap():
    st = ops_state.get()
    now = datetime.now(IST)
    last_tick = None
    tick_age_s = None
    if st.last_tick_ok:
        try:
            last_tick = datetime.fromisoformat(st.last_tick_ok)
            tick_age_s = (now - last_tick).total_seconds()
        except Exception:
            pass
    return {
        "t": now.isoformat(timespec="seconds"),
        "paused": st.paused, "halted": st.halted,
        "halt_reason": st.halt_reason,
        "tick_age_s": tick_age_s,
        "llm_calls_today": st.llm_calls_today,
        "errors_this_hour": st.errors_this_hour,
        "last_error": st.last_error,
        "quarantined": list(st.quarantined.keys()),
        "consecutive_losses": {k: v for k, v in st.consecutive_losses.items() if v > 0},
        "last_deliberation": {k: v[-8:] for k, v in st.last_deliberation.items()},
        "day_realized_pnl": st.day_realized_pnl,
    }

def main(interval=15, duration=600):
    end = time.time() + duration
    while time.time() < end:
        print(json.dumps(snap()), flush=True)
        time.sleep(interval)

if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    main(interval, duration)

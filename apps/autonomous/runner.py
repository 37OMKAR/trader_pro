"""
Non-stop supervisor for the autonomous firm.

Runs `python -m apps.autonomous.scheduler` as a child process. If the child
exits cleanly, the runner exits too. If the child crashes, the runner waits
`backoff_seconds` (exponential up to a cap), re-checks the kill switch, and
relaunches — indefinitely.

Honors the kill switch:
  - When ops/state.json has halted=True, the child scheduler already refuses
    new orders. The runner still keeps the process alive so the position
    tick keeps protecting open stops. To fully stop the runner too, set the
    HERMES_RUNNER_STOP file (default ./ops/runner.stop) — the runner checks
    for it on every restart cycle and exits cleanly if present.

Usage:
  python -m apps.autonomous.runner --symbols RELIANCE TCS HDFCBANK [--skip-hours-gate]
"""

from __future__ import annotations
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

STOP_FILE = Path(os.getenv("HERMES_RUNNER_STOP", "ops/runner.stop"))
MAX_BACKOFF = 300  # 5 minutes


def _spawn(scheduler_args: list) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    cmd = [sys.executable, "-u", "-m", "apps.autonomous.scheduler", *scheduler_args]
    return subprocess.Popen(cmd, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes Autonomous Firm — non-stop runner")
    parser.add_argument("--symbols", nargs="*", default=None,
                        help="Watchlist symbols. Persisted to ops.state.watchlist.")
    parser.add_argument("--skip-hours-gate", action="store_true",
                        help="Passed through to the scheduler.")
    parser.add_argument("--initial-backoff", type=int, default=10)
    parser.add_argument("--max-restarts", type=int, default=0,
                        help="0 = unlimited (default). Non-zero caps for testing.")
    args = parser.parse_args()

    scheduler_args = []
    if args.skip_hours_gate:
        scheduler_args.append("--skip-hours-gate")
    if args.symbols:
        scheduler_args.extend(["--symbols", *args.symbols])

    restarts = 0
    backoff = max(1, args.initial_backoff)
    print(f"[RUNNER] Supervising scheduler; stop file: {STOP_FILE}")

    # Forward SIGINT/SIGTERM to the child.
    child_ref = {"proc": None}

    def _forward(signum, _frame):
        child = child_ref["proc"]
        if child and child.poll() is None:
            try:
                child.send_signal(signum)
            except Exception:
                pass

    for sig in ("SIGINT", "SIGTERM"):
        s = getattr(signal, sig, None)
        if s is not None:
            try:
                signal.signal(s, _forward)
            except (ValueError, OSError):
                pass

    while True:
        if STOP_FILE.exists():
            print(f"[RUNNER] Stop file {STOP_FILE} present — exiting cleanly.")
            return 0

        proc = _spawn(scheduler_args)
        child_ref["proc"] = proc
        started = time.time()
        print(f"[RUNNER] Scheduler pid={proc.pid} launched (restart #{restarts}).")

        rc = proc.wait()
        elapsed = time.time() - started
        print(f"[RUNNER] Scheduler pid={proc.pid} exited rc={rc} after {elapsed:.1f}s.")

        if rc == 0:
            print("[RUNNER] Clean exit — supervisor exiting too.")
            return 0

        restarts += 1
        if args.max_restarts and restarts >= args.max_restarts:
            print(f"[RUNNER] max-restarts {args.max_restarts} reached — giving up.")
            return 1

        # Exponential backoff — reset if the crash happened after > 5 min uptime (looked healthy).
        if elapsed > 300:
            backoff = max(1, args.initial_backoff)
        else:
            backoff = min(MAX_BACKOFF, backoff * 2)
        print(f"[RUNNER] Sleeping {backoff}s before restart.")
        time.sleep(backoff)


if __name__ == "__main__":
    sys.exit(main())

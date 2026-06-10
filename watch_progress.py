"""watch_progress.py — live console view of the studio's progress feed.

Tails `workspace/.progress.jsonl` (written by the lifecycle callbacks in
`agent.py`) and prints each agent/tool start & finish as an indented, timestamped
tree, so you can watch the agents work in REAL TIME — including inside
`studio_pipeline`, whose events the `adk web` Events tab hides because the whole
build runs as one nested `AgentTool` call.

Run in a SECOND terminal while an `adk web` run or a console harness is going:

    python watch_progress.py            # follow only new activity (default)
    python watch_progress.py --all      # replay the whole feed first, then follow
    python watch_progress.py --clear    # truncate the feed, then follow

No third-party dependencies. Ctrl+C to stop.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

FEED = Path(__file__).parent / "workspace" / ".progress.jsonl"


def _fmt(rec: dict) -> str | None:
    """Render one feed record, or None to skip it (keeps the view readable)."""
    kind = rec.get("kind", "")
    name = rec.get("name", "?")
    t = rec.get("t", "")
    indent = "  " * int(rec.get("depth", 0) or 0)
    if kind == "agent_start":
        return f"{t}  {indent}▶ {name}"          # ▶ agent begins
    if kind == "agent_end":
        return f"{t}  {indent}■ {name} done"     # ■ agent finished
    if kind == "tool_start":
        return f"{t}  {indent}  → {name}()"      # → tool invoked
    if kind == "tool_end":
        return None                                    # hide tool returns (noisy)
    return f"{t}  {indent}{kind} {name}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Live view of the ADK studio progress feed.")
    ap.add_argument("--all", action="store_true", help="replay existing feed before following")
    ap.add_argument("--clear", action="store_true", help="truncate the feed before following")
    args = ap.parse_args()

    FEED.parent.mkdir(parents=True, exist_ok=True)
    if args.clear:
        FEED.write_text("", encoding="utf-8")

    print(f"watching {FEED}  (Ctrl+C to stop)\n", flush=True)
    while not FEED.exists():  # the feed appears once the first agent runs
        time.sleep(0.3)

    with FEED.open("r", encoding="utf-8") as f:
        if not args.all:
            f.seek(0, 2)  # jump to EOF: follow only newly appended lines
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.25)
                continue
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            out = _fmt(rec)
            if out is not None:
                print(out, flush=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nstopped.")

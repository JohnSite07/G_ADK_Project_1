"""Run the FULL website build pipeline from the console (no web server).

Streams every phase, tool call, and tool result as it happens, then lists the
generated workspace. Press Ctrl+C any time to stop cleanly (e.g. if an npm/
terraform subprocess stalls) without taking down a server.

Usage:
    python run_pipeline.py                 # uses the default brief below
    python run_pipeline.py "your brief"    # custom brief
"""
import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types

import agent as studio  # loads .env, defines the agents

PIPELINE = studio.website_build_pipeline
DEFAULT_BRIEF = (
    "Build an engaging, production-grade website that invites people to visit "
    "natural places (forests, mountains, lakes) with scroll-driven animations, "
    "a 3D hero scene, and an animated chart of visitor numbers."
)


def _short(v, n=70):
    s = str(v)
    return s if len(s) <= n else s[:n] + "…"


async def main() -> None:
    brief = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BRIEF
    runner = InMemoryRunner(agent=PIPELINE, app_name="pipeline")
    session = await runner.session_service.create_session(app_name="pipeline", user_id="u1")
    msg = types.Content(role="user", parts=[types.Part(text=brief)])

    print(f"\n=== Running '{PIPELINE.name}' ===")
    print(f"Brief: {brief}\n")
    current = None
    async for event in runner.run_async(user_id="u1", session_id=session.id, new_message=msg):
        if event.author != current:
            current = event.author
            print(f"\n----- phase/agent: {current} -----")
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            if part.function_call:
                fc = part.function_call
                args = {k: _short(v) for k, v in (fc.args or {}).items()}
                print(f"  TOOL CALL  -> {fc.name}({args})")
            elif part.function_response:
                print(f"  TOOL RESULT <- {_short(part.function_response.response, 140)}")
            elif part.text and part.text.strip():
                print(f"  SAYS: {_short(part.text.strip(), 300)}")

    print("\n=== Workspace contents ===")
    ws = studio.WORKSPACE
    files = sorted(p for p in ws.rglob("*") if p.is_file())
    if not files:
        print("(empty)")
    for p in files:
        print(f"  {p.relative_to(ws)}  ({p.stat().st_size} bytes)")
    print(f"\nDone. Full output is under: {ws}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[interrupted] stopped by user.")

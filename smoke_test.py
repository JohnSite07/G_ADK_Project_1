"""Quick smoke test: run ONE agent through ADK's Runner to prove the
agent -> tool -> file-write loop actually works end to end on Vertex.

Run:  python smoke_test.py
"""
import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

import agent as studio  # loads .env, defines the agents

TEST_AGENT = studio.requirements_analyst  # cheapest phase: writes docs/spec.md
BRIEF = (
    "Build an interactive website that invites people to visit natural places "
    "(forests, mountains, lakes). Keep the spec short."
)


async def main() -> None:
    runner = InMemoryRunner(agent=TEST_AGENT, app_name="smoke")
    session = await runner.session_service.create_session(app_name="smoke", user_id="u1")

    msg = types.Content(role="user", parts=[types.Part(text=BRIEF)])
    print(f"\n=== Running '{TEST_AGENT.name}' through ADK Runner ===\n")

    async for event in runner.run_async(user_id="u1", session_id=session.id, new_message=msg):
        author = event.author
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            if part.function_call:
                fc = part.function_call
                preview = {k: (str(v)[:60] + "…" if len(str(v)) > 60 else v) for k, v in (fc.args or {}).items()}
                print(f"[{author}] TOOL CALL -> {fc.name}({preview})")
            elif part.function_response:
                print(f"[{author}] TOOL RESULT <- {str(part.function_response.response)[:120]}")
            elif part.text and part.text.strip():
                print(f"[{author}] SAYS: {part.text.strip()[:400]}")

    print("\n=== Workspace contents after run ===")
    ws = studio.WORKSPACE
    found = list(ws.rglob("*"))
    if not found:
        print("(empty — no files written)")
    for p in found:
        if p.is_file():
            print(f"  {p.relative_to(ws)}  ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    asyncio.run(main())

"""Continue an in-progress build from the existing workspace/docs/.

The requirements + design phases were already completed (docs/spec.md,
docs/design-system.md, docs/motion-spec.md exist). This harness skips them:
it seeds those documents into shared session state and runs only the remaining
phases — frontend -> backend -> database -> devops -> qa — reusing the agents
defined in agent.py.

Usage:  python run_continue.py
Ctrl+C stops cleanly (e.g. if an npm/terraform subprocess stalls).
"""
import asyncio

from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

import agent as studio  # loads .env, defines the agents

DOCS = studio.WORKSPACE / "docs"


def _read(name: str) -> str:
    f = DOCS / name
    return f.read_text(encoding="utf-8") if f.exists() else ""


def _short(v, n=70):
    s = str(v)
    return s if len(s) <= n else s[:n] + "…"


async def main() -> None:
    spec = _read("spec.md")
    design = _read("design-system.md")
    motion = _read("motion-spec.md")
    if not spec:
        print("No docs/spec.md found — nothing to continue from. Run run_pipeline.py instead.")
        return

    # Remaining phases. Detach them from website_build_pipeline so they can be
    # composed into this continuation pipeline (ADK forbids two parents).
    remaining = [
        studio.frontend_lead,
        studio.backend_engineer,
        studio.database_architect,
        studio.devops_engineer,
        studio.qa_reviewer,
    ]
    for a in remaining:
        a.parent_agent = None
    continuation = SequentialAgent(
        name="continuation_build",
        description="Resume the build from the frontend using existing docs.",
        sub_agents=remaining,
    )

    # Seed shared state ("whiteboard") with the already-approved artifacts so the
    # downstream agents read them instead of regenerating.
    seed_state = {"spec": spec, "design_spec": f"{design}\n\n---\n\n{motion}"}

    runner = InMemoryRunner(agent=continuation, app_name="continue")
    session = await runner.session_service.create_session(
        app_name="continue", user_id="u1", state=seed_state
    )

    kickoff = (
        "The product spec and design/motion specs are ALREADY complete and are "
        "available in your session state (keys 'spec' and 'design_spec') and as "
        "files under docs/ (spec.md, design-system.md, motion-spec.md). Do NOT "
        "redefine them. Read them and continue the build: implement the frontend "
        "(with the animation/3D/dataviz specialists), then backend, database, "
        "Terraform infra on Google Cloud, and finally QA."
    )
    msg = types.Content(role="user", parts=[types.Part(text=kickoff)])

    print("\n=== Continuing build from docs/ ===")
    print(f"Seeded state keys: {list(seed_state)}  | phases: {[a.name for a in remaining]}\n")
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
    for p in sorted(x for x in ws.rglob("*") if x.is_file()):
        print(f"  {p.relative_to(ws)}  ({p.stat().st_size} bytes)")
    print(f"\nDone. Output under: {ws}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[interrupted] stopped by user.")

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project goal

Build a **group of cooperating Google ADK agents** that together produce production-grade websites with
highly interactive UIs — scroll-driven animations, animated graphs, 3D scenes, and dynamic data
visualizations (reference target: https://ai.google/our-ai-journey/). The agents own the full pipeline:
animation/interaction design → frontend → backend → database → DevOps. Hosting infrastructure is
provisioned with **Terraform** (in a `terraform/` folder, generated into the workspace) and **must target
Google Cloud**. This is a testbed for evaluating Google ADK's multi-agent efficiency, so prefer ADK-native
constructs (`LlmAgent`, `SequentialAgent`, `LoopAgent`, sub-agents, tools, `AgentTool`) over custom
orchestration.

## Status

Working multi-agent studio in `agent.py`, **run end-to-end twice** (2026-06-06), both archived under
`archive/` (`workspace-2026-06-06-run1`, `-run2`). Run 2 ("code ideas about the universe"): the
`refinement_loop` recovered a botched frontend (build_fixer implemented the real components) → green build +
valid GCP Terraform + Dockerfile + CI/CD; browser UAT then ran (after the async/Playwright fixes) and found
the animations/3D didn't work at runtime → a new `uat_loop` (uat_tester ↔ uat_fixer) was added to
self-correct that. See Lessons learned. `agent.py` is hardened after each run; `workspace/` is regenerated
empty on import.

## Environment & tooling

- **Python**: 3.13, default interpreter `C:\Program Files\Python313\python.exe`.
- **google-adk**: 2.2.0, installed to the **per-user** site-packages
  (`C:\Users\ASUS\AppData\Roaming\Python\Python313`). Upgrade with `python -m pip install --upgrade google-adk`.
- **`adk` CLI**: at `C:\Users\ASUS\AppData\Roaming\Python\Python313\Scripts\adk.exe` (Scripts dir **not on
  PATH** — use the full path or `python -m google.adk.cli`). Verify with `adk --version`.
- **Model access = Vertex AI** (`.env`): `GOOGLE_GENAI_USE_VERTEXAI=TRUE`,
  `GOOGLE_CLOUD_PROJECT=project-815cbb1b-9505-4ce3-bc4`, `GOOGLE_CLOUD_LOCATION=global` (widest model
  availability). `GOOGLE_CLOUD_REGION`/`ZONE` (Toronto) are for the generated Terraform, not the SDK.
  Vertex uses **ADC**, not the API key: run `gcloud auth application-default login` and ensure the Vertex AI
  API is enabled on the project. The legacy `GOOGLE_API_KEY` is kept only as a fallback.
- **Models** (env-overridable): `GADK_PRO_MODEL` (default `gemini-2.5-pro`), `GADK_FLASH_MODEL`
  (default `gemini-2.5-flash`). `agent.py` uses PRO for every phase.
- **Playwright** (for the UAT agent's browser tools) is optional and lazy-imported. Before a UAT run:
  `python -m pip install playwright ; python -m playwright install chromium`.
- **Known machine issue**: pip/venv/`npm` operations can hang when the WMI service wedges; fix by restarting
  `Winmgmt` (needs an **admin** shell: `Restart-Service Winmgmt -Force`). Suspect this if an install stalls.

## Common commands

ADK discovers an agent by importing a package exposing a module-level `root_agent`. This folder is that
package (`__init__.py` → `from . import agent`; `agent.py` defines `root_agent`). **Run from the parent
directory** (`...\Google_ADK`) so `G_ADK_Project_1` is importable, and `agent.py` loads its own `.env` by
absolute path so the Vertex project resolves regardless of cwd.

```powershell
cd "c:\Users\ASUS\Desktop\Projects\Agents\Google_ADK"
python -m google.adk.cli web      # dev UI (chat + Events/Traces/State) at http://localhost:8000
python -m google.adk.cli run G_ADK_Project_1
```

Console harnesses (avoid the web server wedging on long builds; stream phases; Ctrl+C is clean):

```powershell
cd "c:\Users\ASUS\Desktop\Projects\Agents\Google_ADK\G_ADK_Project_1"
python smoke_test.py     # one agent (requirements_analyst) — fastest health check
python run_pipeline.py   # full studio_pipeline on a default/CLI brief
python run_continue.py   # RESUME from existing workspace/docs/ (skips requirements+design)
```

There is no test/lint setup. If one is added, document the exact commands here.

## Architecture (`agent.py`)

`root_agent` = **`studio_director`** (conversational `LlmAgent`). Its main tool is `studio_pipeline`; it also
exposes team agents as `AgentTool`s for targeted follow-ups. `studio_pipeline` (`SequentialAgent`) runs:

1. **`website_build_pipeline`** (`SequentialAgent`): `requirements_analyst` → `ux_design_director` →
   `frontend_lead` → `backend_engineer` → `database_architect` → `devops_engineer`.
   - `frontend_lead` orchestrates three specialists as `AgentTool`s: `animation_engineer` (scroll/GSAP/
     Framer Motion), `threed_engineer` (react-three-fiber), `dataviz_engineer` (D3/visx). It MUST delegate
     to all three (one per motion-spec category) and self-verify with `npm run build`.
2. **`refinement_loop`** (`LoopAgent`, max 3): `qa_reviewer` (critic — runs `npm run build`, checks spec/
   motion coverage; calls `exit_loop` when green with no P0/P1) ↔ `build_fixer` (applies `docs/qa-report.md`).
3. **`uat_loop`** (`LoopAgent`, max 3): `uat_tester` (critic — boots the app via `start_dev_server`, drives
   the real UI in a headless browser with Playwright, verifies each spec'd interaction at RUNTIME, writes
   `docs/uat-report.md` + screenshots under `workspace/uat/`; calls `exit_loop` when every journey passes) ↔
   `uat_fixer` (fixes the runtime UI failures uat_tester reports, then re-builds). This makes browser
   failures self-correcting instead of needing manual relay to `frontend_lead`.
4. **`compliance_auditor`**: audits **agent behavior** (did each phase follow its instructions/spec?), not
   code quality — writes `docs/compliance-report.md`. This is deliberately separate from `qa_reviewer`.

Phases communicate via shared session state ("whiteboard") `output_key`s: `spec`, `design_spec`, `frontend`,
`backend`, `database`, `infra`, `qa_report`, `uat_report`, `compliance_report`. Specialists also read/write
the `docs/` files.

### Tools (all in `agent.py`, workspace-confined via `_safe`)
- File: `write_file`, `read_file`, `list_directory`.
- Shell: `run_command` — **runs via PowerShell** (use PS/cross-platform syntax, not bash-isms).
- Infra: `run_terraform` (wraps `terraform` in `workspace/terraform/`).
- Dev server: `start_dev_server` / `stop_dev_server` (background, polls the port).
- Browser/UAT: `uat_open`, `uat_screenshot`, `uat_interact`, `uat_close` — Playwright **sync** API run on a
  single dedicated worker thread (see lesson below); async tool wrappers hand work to that thread.

Tool descriptions/docstrings are what the model routes on — keep them specific and action-oriented.

### ADK version note
`SequentialAgent`/`LoopAgent` are **deprecated in 2.2.0** (favoring graph `Workflow`) but kept deliberately:
they are functional and are `BaseAgent`s, so they compose with `AgentTool`/`sub_agents`; `Workflow` is not a
`BaseAgent`. An agent instance may have only ONE structural parent — reuse via `AgentTool` references, not by
adding it to a second pipeline (see `run_continue.py`, which detaches agents to recompose them).

## Lessons learned (run 1 → why output was a weak draft, and the fixes applied)

- **Frontend missed the interactivity** (the headline goal): `frontend_lead` only delegated to
  `dataviz_engineer`, never `animation_engineer`/`threed_engineer`, so no parallax/3D/scroll work shipped.
  → Instruction now mandates delegating to all three and covering every `motion-spec.md` item.
- **Broken build reached QA**: the frontend never self-verified. → `npm run build` is now mandatory in
  `frontend_lead`, plus the `refinement_loop` (build_fixer ↔ qa critic) iterates until green.
- **`mkdir -p` and other bash-isms failed** under the old `cmd.exe` shell. → `run_command` now uses
  PowerShell.
- **Interactive-prompt deadlock**: `npx create-next-app@<pinned-version>` (uncached) prompts "Ok to
  proceed? (y)" and blocked forever because `run_command` gave the child no stdin — the whole `adk web`
  server wedged behind it (only `docs/` ever appeared). → `run_command` now runs with
  `stdin=DEVNULL` and `CI=1` / `npm_config_yes=true`, so prompts auto-confirm or EOF instead of hanging.

### Run 2 (2026-06-06, "code ideas about the universe") — the new safety nets worked
- **`frontend_lead` integration failure**: it delegated to the specialists but then wrote **empty
  placeholder** components, ignoring/overwriting their output (it acted on "done" confirmations without
  reading the files). → Caught automatically by the `refinement_loop`: `qa_reviewer` FAILED the build and
  `build_fixer` re-implemented all five interactive components + fixed two TS errors → green build. The
  `compliance_auditor` pinpointed the exact deviation. Fix applied: `frontend_lead` now must let specialists
  write the files, then `read_file` each to confirm it's a real implementation (no self-authored stubs).
- **UAT tool bug**: browser tools used Playwright's **sync** API, which errors inside ADK's asyncio loop
  ("use the Async API instead"). → Rewritten with `playwright.async_api` (`uat_*` and `start_dev_server`
  are now `async def`). Playwright is installed; if missing, `uat_open` returns an actionable message.
- **Takeaway**: the loop + UAT + compliance trio is earning its keep — the loop salvaged a botched build, and
  the auditor produced precise, actionable fixes for both an agent (frontend_lead) and the tooling (uat_open).
- **Corrupt binary/media assets** (after the async UAT fix let UAT actually run): the `threed_engineer`
  hand-authored a `galaxy.gltf` 3D model, which an LLM cannot produce validly — the browser threw a JSON parse
  error and the director↔frontend_lead↔UAT loop could not converge (every regenerated `.gltf` was corrupt or a
  951-byte stub). → Rule added to `HOUSE_STYLE` (never fabricate binary/media assets) and `threed_engineer`
  now builds ALL geometry procedurally (THREE.Points/BufferGeometry/meshes), never authoring `.gltf`/`.glb`.
- **Playwright async API failed inside `adk web`** with "Connection closed while reading from the driver"
  (the async driver subprocess clashes with uvicorn's event loop on Windows — even though standalone
  `asyncio.run` works). → Browser tools rewritten to use the **sync** API on a single dedicated worker
  thread (`_PW_EXEC`, max_workers=1) with async wrappers; verified working when awaited inside a running
  loop. A new playwright version can also "vanish" if installed into a different interpreter than the one
  adk runs on — install into the same Python that has `google-adk` (the default user-site interpreter).
- **UI visibility**: because `studio_pipeline` runs as an `AgentTool` on the director, its internal events do
  NOT appear in the dev UI **Events** tab (only the outer tool call/return do) — use the **Traces** tab (full
  nested span tree), the **State** tab, or watch `workspace/` for live progress. This is expected, not a bug.
- **Director reporting bug**: `studio_director` had no file tools and claimed it would "monitor" an
  already-finished synchronous run. → Gave it `FILE_TOOLS` and instructed it that tool calls are synchronous
  (when they return, work is done) so it reads the report files and summarizes real results.
- **`--legacy-peer-deps` masked a missing peer dep** (`prop-types`), failing the build later. → fixer guidance
  + build verification catch this.
- **Specialists wrote to `frontend/src/`** while the lead used the App Router `app/`/`components/`, causing
  duplicate components. → all specialists now target `app/`/`components/`.
- **Vertex project mismatch**: `adk web` (launched from the parent dir) didn't load the package `.env`, so the
  client fell back to the ADC default project and 403'd. → `agent.py` loads its `.env` by absolute path with
  `override=True`.

## Conventions

- Secrets live only in `.env`. Never hardcode credentials. Terraform must target Google Cloud.
- **Deployment is manual and gated.** Agents author + `terraform validate` only; they NEVER run `apply`.
  `devops_engineer` generates a single-run `workspace/deploy.ps1` (prereq checks → init → plan → one
  confirmation → targeted apply for APIs/Artifact Registry → Cloud Build image push → full apply → prints
  the Cloud Run URL). The user runs `./deploy.ps1` when ready; nothing is on GCP until they do.
- Pin model IDs via the `GADK_*` env vars / the constants at the top of `agent.py`.
- Generated artifacts go under `workspace/`; archive completed runs under `archive/` (exclude
  `node_modules`/`.next`/`.git`/`.terraform` — they're regenerable).

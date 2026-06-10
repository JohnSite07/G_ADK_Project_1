"""
G_ADK_Project_1 — a cooperative multi-agent "web studio" built on Google ADK.

Goal
----
A group of specialist agents that, working together, design and build
production-grade websites with highly interactive UIs: scroll-driven
animations, animated/moving graphs, 3D scenes, and dynamic data
visualizations (reference: https://ai.google/our-ai-journey/). The team owns
the full pipeline — interaction/animation design, frontend, backend, database,
and DevOps (Terraform) — and writes real files into a workspace via tools.

Architecture
------------
                       ┌──────────────────────────┐
                       │  studio_director (root)   │  conversational coordinator
                       └────────────┬─────────────┘
                                    │ AgentTool
                       ┌────────────▼─────────────┐
                       │  website_build_pipeline   │  SequentialAgent (fixed phases)
                       └────────────┬─────────────┘
   requirements → design → FRONTEND LEAD → backend → database → devops → qa
                                    │
                         AgentTools │ (animation / 3D / dataviz specialists)

- The pipeline runs the deterministic build phases in order; each phase writes
  its artifact to shared session state (the "whiteboard") via `output_key`,
  so later phases read what earlier phases produced.
- The frontend lead orchestrates three UI specialists as AgentTools, calling
  whichever a given build needs (often all three).
- The root is a normal LlmAgent so the `adk web` chat UI feels natural; it can
  run the whole pipeline or target the frontend / devops for follow-up tweaks.

Run
---
    adk web        # from this folder's PARENT — pick "G_ADK_Project_1"
    adk run .      # or run this package directly

Requires GOOGLE_API_KEY in .env with the Generative Language API enabled
(or GOOGLE_GENAI_USE_VERTEXAI=TRUE + GOOGLE_CLOUD_PROJECT/LOCATION for Vertex).
"""

from __future__ import annotations

import asyncio
import atexit
import concurrent.futures
import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path

from dotenv import load_dotenv

# NOTE: ADK 2.2.0 marks SequentialAgent and LoopAgent as deprecated in favor of
# the new graph-based `google.adk.workflow.Workflow`. We deliberately keep them
# here: both are fully functional in 2.2.0, are BaseAgents (so they compose with
# AgentTool/sub_agents as used below), and are the idiomatic, well-documented way
# to express fixed pipelines / refinement loops. `Workflow` is not a BaseAgent,
# so migrating would require reworking the coordinator wiring.
# Migration path when these are removed: model each phase as a node and chain
# them with edges, e.g.
#     from google.adk.workflow import Workflow, START
#     website_build_pipeline = Workflow(name=..., description=..., edges=[
#         (START, requirements_analyst), (requirements_analyst, ux_design_director), ...])
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import AgentTool, FunctionTool, exit_loop

# Load THIS package's .env explicitly (override=True) so GOOGLE_CLOUD_PROJECT /
# LOCATION are set no matter what cwd `adk web` is launched from. Without the
# explicit path, a bare load_dotenv() searches from cwd and misses this file's
# .env when adk is run from the parent folder — the Vertex client then falls
# back to the ADC default project and 403s on a project that lacks the API.
load_dotenv(Path(__file__).parent / ".env", override=True)

# --------------------------------------------------------------------------- #
# Models — override via .env.                                                  #
# --------------------------------------------------------------------------- #
# GADK_PROVIDER selects the backend for the PRO model that EVERY phase uses:
#   "claude" (default) -> Anthropic Claude Opus 4.8 on Vertex AI, via ADK's
#                         LiteLlm wrapper (requires `python -m pip install litellm`).
#   "gemini"           -> Vertex AI Gemini (the original gemini-2.5-pro).
# Flip with GADK_PROVIDER=gemini to revert without touching code.
GADK_PROVIDER = os.getenv("GADK_PROVIDER", "claude").strip().lower()

GEMINI_PRO_MODEL = os.getenv("GADK_PRO_MODEL", "gemini-2.5-pro")   # deep reasoning / codegen
FLASH_MODEL = os.getenv("GADK_FLASH_MODEL", "gemini-2.5-flash")    # fast, high-volume (Gemini)

# Claude-on-Vertex model id (BARE — as Vertex / AnthropicVertex expect, no provider
# prefix). Opus 4.8 is served from Vertex AI's **global** endpoint, so the existing
# .env `GOOGLE_CLOUD_LOCATION=global` works as-is (ADK's Claude reads GOOGLE_CLOUD_
# PROJECT/LOCATION directly). Just enable the model in Vertex AI Model Garden first.
# If 4.8 isn't available, set GADK_CLAUDE_MODEL=claude-opus-4-7 (or claude-sonnet-4-6).
CLAUDE_MODEL_ID = os.getenv("GADK_CLAUDE_MODEL", "claude-opus-4-8")
CLAUDE_MAX_TOKENS = int(os.getenv("GADK_CLAUDE_MAX_TOKENS", "16000"))


def _resolve_pro_model():
    """The model every phase runs on: a Gemini model-id string, or — when
    GADK_PROVIDER=claude — ADK's native Claude (the AnthropicVertex SDK) on Vertex AI.
    Construction is cheap (no network); the first real Vertex call happens at run time."""
    if GADK_PROVIDER == "claude":
        try:
            from google.adk.models.anthropic_llm import Claude
        except ImportError as e:  # noqa: BLE001
            raise RuntimeError(
                "GADK_PROVIDER=claude needs the Anthropic Vertex SDK: "
                '`python -m pip install "anthropic[vertex]"`. '
                "Or set GADK_PROVIDER=gemini to use Vertex Gemini."
            ) from e
        # ADK's Claude builds AsyncAnthropicVertex(project=GOOGLE_CLOUD_PROJECT,
        # region=GOOGLE_CLOUD_LOCATION) — the same client + 'global' endpoint as the
        # Model Garden snippet. It sends NO temperature/top_p and NO thinking param by
        # default, so Opus 4.8 (which 400s on both) is happy out of the box. To enable
        # adaptive thinking later, give the agents a generate_content_config with
        # thinking_budget=-1 (and output_config.effort via the model's effort knob).
        return Claude(model=CLAUDE_MODEL_ID, max_tokens=CLAUDE_MAX_TOKENS)
    return GEMINI_PRO_MODEL


PRO_MODEL = _resolve_pro_model()

# --------------------------------------------------------------------------- #
# Workspace — all file/shell tools are confined to this directory so agents    #
# can't write outside the generated project.                                   #
# --------------------------------------------------------------------------- #
WORKSPACE = Path(os.getenv("GADK_WORKSPACE", Path(__file__).parent / "workspace")).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)


def _safe(path: str) -> Path:
    """Resolve `path` inside WORKSPACE, rejecting traversal outside it."""
    target = (WORKSPACE / path).resolve()
    if target != WORKSPACE and WORKSPACE not in target.parents:
        raise ValueError(f"Path '{path}' escapes the workspace.")
    return target


# --------------------------------------------------------------------------- #
# Live progress feed                                                           #
# --------------------------------------------------------------------------- #
# The `adk web` Events tab only shows the OUTER event stream, so while the whole
# build runs as a single nested `AgentTool` call (studio_pipeline) it appears
# silent until the tool returns. These lifecycle callbacks sidestep that: they
# fire IN-PROCESS as each agent/tool starts and finishes — regardless of how
# deeply nested the AgentTool is — and append one JSON line per event to
# `workspace/.progress.jsonl`. Tail that file (or run `watch_progress.py`) in a
# second terminal to watch the agents work in real time. Telemetry only: a feed
# write must NEVER raise into a run, so every path here swallows errors.
PROGRESS_FEED = WORKSPACE / ".progress.jsonl"
_FEED_LOCK = threading.Lock()
_FEED_DEPTH = [0]  # current agent-nesting depth, maintained by the writer process


def _feed_write(kind: str, name: str, depth: int, **extra) -> None:
    rec = {"t": time.strftime("%H:%M:%S"), "kind": kind, "name": name, "depth": depth}
    rec.update({k: v for k, v in extra.items() if v is not None})
    try:
        with _FEED_LOCK, PROGRESS_FEED.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — telemetry must never break a run
        pass


def _on_agent_start(callback_context):
    depth = _FEED_DEPTH[0]
    _feed_write("agent_start", getattr(callback_context, "agent_name", "?"), depth,
                invocation=getattr(callback_context, "invocation_id", None))
    _FEED_DEPTH[0] = depth + 1
    return None  # returning Content would override the agent's output


def _on_agent_end(callback_context):
    _FEED_DEPTH[0] = max(0, _FEED_DEPTH[0] - 1)
    _feed_write("agent_end", getattr(callback_context, "agent_name", "?"), _FEED_DEPTH[0],
                invocation=getattr(callback_context, "invocation_id", None))
    return None


def _on_tool_start(tool, args, tool_context):
    _feed_write("tool_start", getattr(tool, "name", str(tool)), _FEED_DEPTH[0],
                agent=getattr(tool_context, "agent_name", None))
    return None  # returning a dict would short-circuit the tool


def _on_tool_end(tool, args, tool_context, tool_response):
    _feed_write("tool_end", getattr(tool, "name", str(tool)), _FEED_DEPTH[0],
                agent=getattr(tool_context, "agent_name", None))
    return None


def _register_progress_callbacks(agent, _seen=None) -> None:
    """Attach the feed callbacks to `agent` and everything reachable from it
    (sub_agents + AgentTool-wrapped agents), de-duplicating shared instances so
    an agent referenced from two places (e.g. frontend_lead) is wired once."""
    if _seen is None:
        _seen = set()
    if id(agent) in _seen:
        return
    _seen.add(id(agent))
    try:  # every BaseAgent supports the agent-lifecycle callbacks
        agent.before_agent_callback = _on_agent_start
        agent.after_agent_callback = _on_agent_end
    except Exception:  # noqa: BLE001
        pass
    if hasattr(agent, "before_tool_callback"):  # LlmAgents only
        try:
            agent.before_tool_callback = _on_tool_start
            agent.after_tool_callback = _on_tool_end
        except Exception:  # noqa: BLE001
            pass
    for sub in getattr(agent, "sub_agents", None) or []:
        _register_progress_callbacks(sub, _seen)
    for tool in getattr(agent, "tools", None) or []:
        wrapped = getattr(tool, "agent", None)  # AgentTool wraps an agent
        if wrapped is not None:
            _register_progress_callbacks(wrapped, _seen)


# --------------------------------------------------------------------------- #
# Tools (real implementations). Docstrings + type hints become the schema the  #
# model routes on, so they are written to be specific and action-oriented.     #
# --------------------------------------------------------------------------- #
def write_file(path: str, content: str) -> dict:
    """Create or overwrite a UTF-8 text file inside the project workspace.

    Args:
        path: Workspace-relative path, e.g. 'frontend/src/App.tsx'. Parent
            directories are created automatically.
        content: Full file contents to write (overwrites any existing file).

    Returns:
        A dict with the written path and byte count, or an error.
    """
    try:
        f = _safe(path)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
        return {"status": "ok", "path": str(f.relative_to(WORKSPACE)), "bytes": len(content.encode("utf-8"))}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def read_file(path: str) -> dict:
    """Read a UTF-8 text file from the workspace.

    Args:
        path: Workspace-relative path to the file.

    Returns:
        A dict with the file content, or an error if it does not exist.
    """
    try:
        f = _safe(path)
        return {"status": "ok", "path": path, "content": f.read_text(encoding="utf-8")}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def list_directory(path: str = ".") -> dict:
    """List files and folders at a workspace-relative path (non-recursive).

    Args:
        path: Workspace-relative directory, defaults to the workspace root.

    Returns:
        A dict with 'entries': a list of {name, type} where type is file|dir.
    """
    try:
        d = _safe(path)
        if not d.exists():
            return {"status": "error", "error": f"'{path}' does not exist"}
        entries = [{"name": p.name, "type": "dir" if p.is_dir() else "file"} for p in sorted(d.iterdir())]
        return {"status": "ok", "path": path, "entries": entries}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def run_command(command: str, cwd: str = ".", timeout_seconds: int = 300) -> dict:
    """Run a shell command in the workspace (e.g. npm install, npm run build, git init).

    Commands run through Windows PowerShell, so use PowerShell/cross-platform
    syntax — NOT bash-isms. e.g. use `New-Item -ItemType Directory -Force x`
    instead of `mkdir -p x`, and `;` instead of `&&` to chain. Most CLI tools
    (npm, npx, git, node, python) work the same either way.

    Use for scaffolding, installing dependencies, building, and running tests.
    Long-running dev servers should NOT be started here (they block until the
    timeout) — use start_dev_server / stop_dev_server instead.

    Args:
        command: The PowerShell command line to execute.
        cwd: Workspace-relative working directory for the command.
        timeout_seconds: Max seconds before the command is killed (default 300).

    Returns:
        A dict with exit_code, stdout, and stderr (each truncated to 8000 chars).
    """
    try:
        workdir = _safe(cwd)
        workdir.mkdir(parents=True, exist_ok=True)
        # Non-interactive by construction: stdin=DEVNULL so any prompt gets EOF
        # instead of blocking forever, and CI / npm_config_yes auto-confirm
        # npm/npx prompts (e.g. "Ok to proceed? (y)" from `npx create-next-app`).
        env = os.environ.copy()
        env.update({
            "CI": "1",
            "npm_config_yes": "true",
            "npm_config_fund": "false",
            "npm_config_audit": "false",
        })
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            cwd=str(workdir), capture_output=True, text=True, timeout=timeout_seconds,
            stdin=subprocess.DEVNULL, env=env,
        )
        return {
            "status": "ok",
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": f"command timed out after {timeout_seconds}s"}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def run_terraform(command: str, timeout_seconds: int = 600) -> dict:
    """Run a terraform subcommand inside the workspace 'terraform/' directory.

    Args:
        command: The terraform subcommand and flags, e.g. 'init',
            'validate', 'plan -out=tfplan', 'apply -auto-approve'. Do NOT
            include the leading word 'terraform'.
        timeout_seconds: Max seconds before the command is killed (default 600).

    Returns:
        A dict with exit_code, stdout, and stderr.
    """
    return run_command(f"terraform {command}", cwd="terraform", timeout_seconds=timeout_seconds)


# --------------------------------------------------------------------------- #
# Dev-server tools — for the UAT agent to boot the app in the background        #
# (run_command blocks, so it can't host a long-running server itself).          #
# --------------------------------------------------------------------------- #
_SERVERS: dict[int, subprocess.Popen] = {}


def _port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


async def start_dev_server(command: str = "npm run dev", cwd: str = "frontend",
                           port: int = 3000, ready_timeout: int = 90) -> dict:
    """Start a long-running dev/preview server in the background and wait until it
    accepts connections. Use before running browser UAT checks.

    Args:
        command: Server command, e.g. 'npm run dev' or 'npm run start'.
        cwd: Workspace-relative directory to run it in (usually 'frontend').
        port: TCP port to wait for the server to listen on.
        ready_timeout: Max seconds to wait for the port to come up.

    Returns:
        A dict with the URL once ready, or an error if it never came up.
    """
    try:
        if _port_open(port):
            return {"status": "ok", "url": f"http://localhost:{port}", "note": "already listening"}
        workdir = _safe(cwd)
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            cwd=str(workdir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        _SERVERS[port] = proc
        deadline = time.monotonic() + ready_timeout
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                return {"status": "error", "error": f"server exited early (code {proc.returncode})"}
            if _port_open(port):
                return {"status": "ok", "url": f"http://localhost:{port}"}
            await asyncio.sleep(1.0)
        return {"status": "error", "error": f"server not ready on port {port} after {ready_timeout}s"}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


def stop_dev_server(port: int = 3000) -> dict:
    """Stop a dev server previously started with start_dev_server on `port`."""
    proc = _SERVERS.pop(port, None)
    if proc is None:
        return {"status": "ok", "note": "no tracked server on that port"}
    try:
        proc.terminate()
        return {"status": "ok", "stopped_port": port}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


# --------------------------------------------------------------------------- #
# Browser tools (Playwright) — real UI testing for the UAT agent.               #
#                                                                               #
# IMPORTANT (Windows + async servers): Playwright's ASYNC API fails inside      #
# ADK/uvicorn's event loop with "Connection closed while reading from the       #
# driver" (the driver subprocess transport clashes with the server loop). So we #
# use the SYNC API, but run every call on a single dedicated worker THREAD that  #
# has no asyncio loop — sync Playwright is happy there, and one worker means the #
# browser/page persist safely across tool calls. The async tool wrappers just    #
# hand work to that thread. Playwright is imported lazily so agent.py loads even #
# when it isn't installed. One-time setup before a UAT run:                      #
#     python -m pip install playwright ; python -m playwright install chromium   #
# --------------------------------------------------------------------------- #
_BROWSER: dict[str, object] = {}  # holds 'pw', 'browser', 'page' (touched ONLY in the worker thread)
_CONSOLE_ERRORS: list[str] = []
# Single-worker pool: all Playwright calls run on the SAME loop-free thread.
_PW_EXEC = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="playwright")


async def _in_browser_thread(fn, *args):
    """Run a blocking, sync-Playwright function on the dedicated browser thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_PW_EXEC, fn, *args)


def _sync_ensure_page():
    if _BROWSER.get("page") is not None:
        return _BROWSER["page"]
    from playwright.sync_api import sync_playwright  # lazy import (in worker thread)

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("console", lambda msg: _CONSOLE_ERRORS.append(f"{msg.type}: {msg.text}")
            if msg.type in ("error", "warning") else None)
    page.on("pageerror", lambda exc: _CONSOLE_ERRORS.append(f"pageerror: {exc}"))
    _BROWSER.update(pw=pw, browser=browser, page=page)
    return page


def _sync_open(url: str, wait_until: str) -> dict:
    _CONSOLE_ERRORS.clear()
    page = _sync_ensure_page()
    resp = page.goto(url, wait_until=wait_until, timeout=30000)
    return {
        "status": "ok",
        "http_status": resp.status if resp else None,
        "title": page.title(),
        "console_errors": list(_CONSOLE_ERRORS),
    }


def _sync_screenshot(name: str, full_page: bool) -> dict:
    page = _sync_ensure_page()
    out = _safe(f"uat/{name}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out), full_page=full_page)
    return {"status": "ok", "path": str(out.relative_to(WORKSPACE))}


def _sync_interact(selector: str, action: str, text: str) -> dict:
    page = _sync_ensure_page()
    before = len(_CONSOLE_ERRORS)
    if action == "click":
        page.click(selector, timeout=10000); result = "clicked"
    elif action == "hover":
        page.hover(selector, timeout=10000); result = "hovered"
    elif action == "fill":
        page.fill(selector, text, timeout=10000); result = f"filled with {text!r}"
    elif action == "is_visible":
        result = page.is_visible(selector)
    elif action == "text":
        result = page.inner_text(selector, timeout=10000)
    else:
        return {"status": "error", "error": f"unknown action '{action}'"}
    return {"status": "ok", "action": action, "result": result,
            "new_console_errors": _CONSOLE_ERRORS[before:]}


def _sync_close() -> dict:
    _BROWSER.pop("page", None)
    browser = _BROWSER.pop("browser", None)
    pw = _BROWSER.pop("pw", None)
    if browser:
        browser.close()
    if pw:
        pw.stop()
    return {"status": "ok"}


async def uat_open(url: str, wait_until: str = "networkidle") -> dict:
    """Open a URL in a headless browser and report load status + console errors.

    Args:
        url: Full URL to visit, e.g. 'http://localhost:3000'.
        wait_until: Playwright load state ('load', 'domcontentloaded', 'networkidle').

    Returns:
        A dict with the page title and any console/page errors collected so far.
    """
    try:
        return await _in_browser_thread(_sync_open, url, wait_until)
    except ModuleNotFoundError:
        return {"status": "error", "error": "Playwright not installed. Run: "
                "python -m pip install playwright ; python -m playwright install chromium"}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


async def uat_screenshot(name: str = "screenshot", full_page: bool = True) -> dict:
    """Save a PNG screenshot of the current page to workspace 'uat/<name>.png'."""
    try:
        return await _in_browser_thread(_sync_screenshot, name, full_page)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


async def uat_interact(selector: str, action: str = "click", text: str = "") -> dict:
    """Interact with an element to test UI behavior.

    Args:
        selector: CSS selector for the target element.
        action: One of 'click', 'hover', 'fill', 'is_visible', 'text'.
        text: Value to type when action == 'fill'.

    Returns:
        A dict with the action result (and console errors triggered by it).
    """
    try:
        return await _in_browser_thread(_sync_interact, selector, action, text)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


async def uat_close() -> dict:
    """Close the headless browser and free its resources."""
    try:
        return await _in_browser_thread(_sync_close)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "error": str(e)}


@atexit.register
def _cleanup_runtime() -> None:
    # Best-effort: stop any background dev servers on exit. The browser is closed
    # by the agent via uat_close (and reclaimed when the process exits).
    for proc in _SERVERS.values():
        try:
            proc.terminate()
        except Exception:  # noqa: BLE001
            pass


FILE_TOOLS = [FunctionTool(write_file), FunctionTool(read_file), FunctionTool(list_directory)]
SHELL_TOOLS = [FunctionTool(run_command)]
SERVER_TOOLS = [FunctionTool(start_dev_server), FunctionTool(stop_dev_server)]
BROWSER_TOOLS = [
    FunctionTool(uat_open),
    FunctionTool(uat_screenshot),
    FunctionTool(uat_interact),
    FunctionTool(uat_close),
]

# --------------------------------------------------------------------------- #
# Shared standards applied across every agent in an invocation.                #
# --------------------------------------------------------------------------- #
HOUSE_STYLE = """\
You are part of an elite web studio that ships production-grade, highly
interactive websites (think https://ai.google/our-ai-journey/). Shared rules:
- Write real, complete files into the workspace with the file tools. Never
  output code only in chat when a file is the deliverable.
- Stack of record: Next.js (App Router) + TypeScript + Tailwind CSS for the
  frontend; keep components accessible (semantic HTML, reduced-motion support).
- Read prior phases from session state before acting; do not contradict the
  approved spec or design system.
- Favor performance: lazy-load heavy 3D/dataviz, respect Core Web Vitals,
  and guard animations behind `prefers-reduced-motion`.
- NEVER hand-author binary or media assets — you cannot produce valid 3D models
  (.gltf/.glb), images, videos, audio, or fonts as text; doing so yields corrupt
  files that crash the app. Instead: generate visuals procedurally in code
  (geometry/particles for 3D, CSS/SVG for graphics), or reference a real, public
  CDN URL. If a true binary asset is unavoidable, leave a documented placeholder
  and note it for the user — do not fabricate the bytes.
- Keep your final chat message a short summary of what you produced and where
  (paths). The artifacts live in files and shared state, not in prose."""

# --------------------------------------------------------------------------- #
# Phase 1 — Requirements                                                       #
# --------------------------------------------------------------------------- #
requirements_analyst = LlmAgent(
    name="requirements_analyst",
    model=PRO_MODEL,
    description="Turns a website brief into a concrete, structured product spec.",
    instruction="""Convert the user's brief into a precise build spec. Produce:
- Goal & audience, success criteria.
- Sitemap (pages/sections) and per-section content outline.
- An 'interaction inventory': every scroll-driven animation, 3D scene, moving
  graph, and data visualization the site should have, with what each conveys.
- Non-functional needs (performance budget, accessibility, SEO, devices).
Write this to workspace 'docs/spec.md' and also return it as your message.""",
    tools=FILE_TOOLS,
    output_key="spec",
)

# --------------------------------------------------------------------------- #
# Phase 2 — Design & motion direction                                          #
# --------------------------------------------------------------------------- #
ux_design_director = LlmAgent(
    name="ux_design_director",
    model=PRO_MODEL,
    description="Defines the visual design system and the animation/interaction spec.",
    instruction="""Using the spec in state key 'spec', define:
- A design system: color tokens, typography scale, spacing, layout grid,
  component inventory — as concrete CSS variables / Tailwind theme values.
- A motion spec: for each item in the interaction inventory, specify the
  technique (scroll-driven CSS / GSAP+ScrollTrigger / Lenis smooth scroll /
  react-three-fiber 3D / D3 or visx dataviz), the trigger, easing, duration,
  and the reduced-motion fallback.
Write 'docs/design-system.md' and 'docs/motion-spec.md'. Return a summary.""",
    tools=FILE_TOOLS,
    output_key="design_spec",
)

# --------------------------------------------------------------------------- #
# Phase 3 — Frontend: a lead orchestrating three UI specialists as tools       #
# --------------------------------------------------------------------------- #
animation_engineer = LlmAgent(
    name="animation_engineer",
    model=PRO_MODEL,
    description="Implements scroll-driven animation and motion (GSAP/ScrollTrigger, Lenis, Framer Motion).",
    instruction="""Implement the scroll and motion work from 'docs/motion-spec.md'.
Build reusable React/TypeScript components and hooks (e.g. useScrollProgress,
pinned/parallax sections, reveal-on-scroll). Use GSAP + ScrollTrigger and/or
Lenis for smooth scroll, Framer Motion for component transitions. Always honor
`prefers-reduced-motion`. Write reusable components under 'frontend/components/' (App Router — never 'src/').""",
    tools=FILE_TOOLS,
)

threed_engineer = LlmAgent(
    name="threed_engineer",
    model=PRO_MODEL,
    description="Builds 3D scenes with Three.js / react-three-fiber and drei.",
    instruction="""Implement the 3D scenes called for in the spec using
react-three-fiber (+ drei). Build ALL geometry PROCEDURALLY in code — e.g. a
spiral galaxy or starfield as a THREE.Points / BufferGeometry with positions you
generate in a loop, planets as <mesh> spheres, etc. Do NOT author or load
`.gltf`/`.glb` model files (or any binary model asset) — you cannot produce a
valid one and it will crash the scene with a JSON/parse error. If the spec names
a model file, replace it with equivalent procedural geometry. Only `useGLTF`/load
an external model from a real, reputable public URL if explicitly required.
Keep scenes performant: lazy-load, dispose resources, cap pixel ratio, and
degrade gracefully on low-end/no-WebGL devices. Wire scroll-linked camera/object
motion to the shared scroll progress where the motion spec asks for it. Write
reusable components under 'frontend/components/' (App Router — never 'src/').""",
    tools=FILE_TOOLS,
)

dataviz_engineer = LlmAgent(
    name="dataviz_engineer",
    model=PRO_MODEL,
    description="Builds dynamic, animated data visualizations (D3 / visx / Recharts).",
    instruction="""Implement the moving graphs and data visualizations from the
spec. Prefer visx or D3 for bespoke animated charts; ensure transitions are
smooth, responsive, and accessible (labels, aria, keyboard). Animate on scroll
or data change as the motion spec dictates. Write reusable components under 'frontend/components/' (App Router — never 'src/').""",
    tools=FILE_TOOLS,
)

frontend_lead = LlmAgent(
    name="frontend_lead",
    model=PRO_MODEL,
    description="Scaffolds the Next.js app and integrates animation, 3D, and dataviz specialists into pages.",
    instruction="""You own the frontend. The interactive experience IS the
product — a frontend without the specified animations is a FAILURE, not a draft.

Steps (do ALL of them):
1. If 'frontend/' has no app yet, scaffold a Next.js + TypeScript + Tailwind app
   there with run_command. The App Router uses 'app/' and 'components/' — do NOT
   create a 'src/' tree; tell your specialists to write into 'frontend/app' and
   'frontend/components'.
2. Build the pages/sections from the spec and assemble the layout per the design
   system.
3. Read 'docs/motion-spec.md' and treat EVERY entry as a required deliverable.
   You MUST delegate to ALL THREE specialists, not just one:
     - `animation_engineer` for every scroll/parallax/reveal/transition item,
     - `threed_engineer` for every 3D scene,
     - `dataviz_engineer` for every chart/graph/map.
   Tell each specialist the EXACT file path to write (under 'frontend/components')
   and have THEM write the real implementation with their file tools. Do NOT
   author these components yourself and do NOT create placeholder/stub versions —
   that overwrites their work.
   VERIFICATION (mandatory): after each specialist returns, `read_file` the path
   it was told to create and confirm it contains a real implementation (not empty,
   not a TODO stub). If it is missing or trivial, re-delegate with a sharper brief
   or halt and report — do not paper over it with a placeholder. Only after the
   files are confirmed real do you wire their imports into the pages. If the motion
   spec lists an interaction and no real component implements it, you are not done.
4. Install dependencies with exact, compatible versions; if you must use
   '--legacy-peer-deps', immediately run `npm run build` and add any transitive
   packages it reports missing (e.g. peer deps like 'prop-types').
5. VERIFY before finishing: run `npm run build` and fix every error until it
   exits 0. Do not hand off a frontend that does not build.
Write a summary listing each motion-spec item and the component that implements
it, plus the final build status.""",
    tools=[
        *FILE_TOOLS,
        *SHELL_TOOLS,
        AgentTool(agent=animation_engineer),
        AgentTool(agent=threed_engineer),
        AgentTool(agent=dataviz_engineer),
    ],
    output_key="frontend",
)

# --------------------------------------------------------------------------- #
# Phase 4 — Backend                                                            #
# --------------------------------------------------------------------------- #
backend_engineer = LlmAgent(
    name="backend_engineer",
    model=PRO_MODEL,
    description="Implements the backend/API services the frontend needs.",
    instruction="""Implement the backend the spec requires (API routes, content
endpoints, data feeds for the visualizations, form handlers, auth if needed).
Default to Next.js Route Handlers / server actions unless the spec calls for a
separate service. Define clear, typed request/response contracts and document
them. Write files under 'backend/' or 'frontend/app/api/' as appropriate.""",
    tools=[*FILE_TOOLS, *SHELL_TOOLS],
    output_key="backend",
)

# --------------------------------------------------------------------------- #
# Phase 5 — Database                                                           #
# --------------------------------------------------------------------------- #
database_architect = LlmAgent(
    name="database_architect",
    model=PRO_MODEL,
    description="Designs the data model, schema, and migrations.",
    instruction="""Design the persistence layer for the backend's contracts.
Produce an ER overview, a concrete schema (default: PostgreSQL), and migrations
(default: Prisma or SQL). Add seed data where it helps the dataviz. Keep it
normalized but pragmatic. Write files under 'database/' (and a Prisma schema
under 'backend/' if used). Return a summary of tables and relationships.""",
    tools=FILE_TOOLS,
    output_key="database",
)

# --------------------------------------------------------------------------- #
# Phase 6 — DevOps / Terraform                                                 #
# --------------------------------------------------------------------------- #
devops_engineer = LlmAgent(
    name="devops_engineer",
    model=PRO_MODEL,
    description="Provisions hosting infrastructure with Terraform and sets up CI/CD.",
    instruction="""Author Terraform to host this site on **Google Cloud**
(Cloud Run for the app, Artifact Registry for the image, managed Postgres if the
database phase needs one). Write modular .tf files under 'terraform/' (providers,
variables, main, outputs) with sensible variables and no hardcoded secrets. Add a
CI/CD workflow (GitHub Actions). Run `terraform validate` (via run_terraform) and
fix errors.

You MUST also write a single-run, manually-invoked deploy script at
'deploy.ps1' (workspace root, PowerShell). It is the ONE command the user runs
when ready to go live, and must, in order:
  1. Check prerequisites (gcloud + terraform on PATH, an active gcloud login) and
     read project/region from GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_REGION (with
     params to override).
  2. `terraform init`, then `terraform plan` shown for review.
  3. Ask for ONE explicit confirmation (warn that billable resources will be
     created); support an -AutoApprove switch.
  4. Targeted `terraform apply` to enable APIs + create Artifact Registry FIRST
     (the Cloud Run image must exist before the service applies).
  5. Build & push the image with Cloud Build (`gcloud builds submit <app> --tag`)
     so no local Docker is required.
  6. Full `terraform apply`, then print the live service URL.
  Make it idempotent (safe to re-run to redeploy) and stop on the first error.

NEVER run `terraform apply` or the deploy script yourself — generating and
validating is your job; deploying is the user's explicit, manual step. Summarize
the resources and tell the user exactly how to deploy: `./deploy.ps1`.""",
    tools=[*FILE_TOOLS, *SHELL_TOOLS, FunctionTool(run_terraform)],
    output_key="infra",
)

# --------------------------------------------------------------------------- #
# The build pipeline (phases 1–6). QA/UAT/audit run after it, below.           #
# --------------------------------------------------------------------------- #
website_build_pipeline = SequentialAgent(
    name="website_build_pipeline",
    description="Builds the site end to end: requirements → design → frontend → backend → database → devops.",
    sub_agents=[
        requirements_analyst,
        ux_design_director,
        frontend_lead,
        backend_engineer,
        database_architect,
        devops_engineer,
    ],
)

# --------------------------------------------------------------------------- #
# Phase 7 — Refinement loop: QA critic <-> fixer until the build is green.      #
# qa_reviewer assesses and calls exit_loop when it passes; otherwise it writes  #
# a report that build_fixer acts on, then the loop re-checks (max 3 rounds).    #
# --------------------------------------------------------------------------- #
qa_reviewer = LlmAgent(
    name="qa_reviewer",
    model=PRO_MODEL,
    description="QA critic: checks build health and spec coverage; approves or files actionable issues.",
    instruction="""You are the QA gate. Assess the built site against
'docs/spec.md', 'docs/design-system.md', and 'docs/motion-spec.md'. You MUST run
`npm run build` in 'frontend' and check: build exit code, spec/motion coverage
(is every animation/3D/dataviz item actually implemented?), accessibility,
reduced-motion handling, performance risks, and Terraform validity.

Decision:
- If the build exits 0 AND there are no P0 (blocker) or P1 (high) issues, the
  site PASSES — call the `exit_loop` tool and reply 'APPROVED'.
- Otherwise, write a prioritized, concrete report to 'docs/qa-report.md'
  (P0/P1/P2 with exact files and fixes) for the fixer, and reply with the top
  issues. Do NOT call exit_loop.""",
    tools=[*FILE_TOOLS, *SHELL_TOOLS, exit_loop],
    output_key="qa_report",
)

build_fixer = LlmAgent(
    name="build_fixer",
    model=PRO_MODEL,
    description="Applies the fixes listed in docs/qa-report.md across the codebase and re-verifies the build.",
    instruction="""Read 'docs/qa-report.md' and fix the issues it lists, starting
with P0 then P1. Edit the real files (frontend/backend/database/terraform/CI).
Typical fixes: install missing dependencies, add a Dockerfile, correct the
CI/CD deploy strategy, implement missing animations/interactions, add missing
assets or serve them locally, and address accessibility. After fixing, run
`npm run build` in 'frontend' (and `terraform validate` if infra changed) and
keep fixing until the build exits 0. Summarize what you changed.""",
    tools=[*FILE_TOOLS, *SHELL_TOOLS, FunctionTool(run_terraform)],
)

refinement_loop = LoopAgent(
    name="refinement_loop",
    description="Iterates QA review and fixes until the build passes (or max rounds).",
    max_iterations=3,
    sub_agents=[qa_reviewer, build_fixer],
)

# --------------------------------------------------------------------------- #
# Phase 8 — UAT loop: drive the real UI in a browser, then FIX runtime          #
# failures, repeating until every key journey passes (or max rounds).           #
# uat_tester is the critic (calls exit_loop on a full pass); uat_fixer is the    #
# actor that fixes the runtime issues uat_tester reports.                        #
# --------------------------------------------------------------------------- #
uat_tester = LlmAgent(
    name="uat_tester",
    model=PRO_MODEL,
    description="UAT critic: runs the app, exercises the real UI in a browser, and approves or files runtime issues.",
    instruction="""Acceptance-test the RUNNING product against 'docs/spec.md' and
'docs/motion-spec.md'. Test actual runtime BEHAVIOR, not whether code exists.
Steps:
1. Start the app with start_dev_server ('npm run dev', cwd 'frontend', port 3000).
   If it cannot boot, write that as a P0 blocker to 'docs/uat-report.md' and stop
   (do NOT exit_loop).
2. uat_open http://localhost:3000; record HTTP status, title, console errors.
3. Exercise EVERY key interaction from the spec with uat_interact and verify it
   actually happens at runtime: scroll-reveals must start hidden and animate IN on
   scroll (not be visible from the top); 3D scenes must rotate/hover/click; cards
   and CTAs must open. Capture uat_screenshot of the hero, a mid-scroll state, and
   an interaction state.
4. Always call stop_dev_server when done.

Decision:
- If the app loads AND every key user journey actually works at runtime, it
  PASSES — call `exit_loop` and reply 'UAT APPROVED'.
- Otherwise write 'docs/uat-report.md' with a per-journey PASS/FAIL, the exact
  symptom (e.g. 'Big Bang content is visible at scroll=0; reveal never fires'),
  the likely component/file, and a concrete fix for uat_fixer. Reply with the
  failures. Do NOT call exit_loop.

If a tool reports a missing dependency (e.g. Playwright not installed), mark UAT
as 'not run' (NOT a product defect), quote the tool's EXACT suggested command
verbatim, and call `exit_loop` (the loop cannot fix a host-setup gap). Do not
invent install commands or ask devops_engineer — it is a one-time local setup.""",
    tools=[*FILE_TOOLS, *SERVER_TOOLS, *BROWSER_TOOLS, exit_loop],
    output_key="uat_report",
)

uat_fixer = LlmAgent(
    name="uat_fixer",
    model=PRO_MODEL,
    description="Fixes the runtime UI failures listed in docs/uat-report.md, then re-verifies the build.",
    instruction="""Read 'docs/uat-report.md' and fix the runtime UI failures it
lists (these are behavior bugs the browser found, not build errors). Edit the
real component files under 'frontend/'. Typical fixes:
- Scroll animations that don't fire: wire elements to scroll progress with GSAP
  ScrollTrigger or Framer Motion (whileInView/useScroll); ensure they START
  hidden (opacity/transform) and animate IN, with a prefers-reduced-motion
  fallback.
- 3D interactions missing: add OrbitControls, onPointerOver hover tooltips, and
  clickable objects that open info cards (React state). Keep geometry procedural.
After fixing, run `npm run build` in 'frontend' and keep fixing until it exits 0
(do not introduce a broken build). Summarize what you changed for the next UAT
pass. You do not run the browser — uat_tester re-tests next.""",
    tools=[*FILE_TOOLS, *SHELL_TOOLS],
)

uat_loop = LoopAgent(
    name="uat_loop",
    description="Runs browser UAT and fixes runtime UI failures until every key journey passes (or max rounds).",
    max_iterations=3,
    sub_agents=[uat_tester, uat_fixer],
)

# --------------------------------------------------------------------------- #
# Phase 9 — Compliance audit: did the AGENTS do what they were told?           #
# This is distinct from QA (which judges the code). It judges agent BEHAVIOR.   #
# --------------------------------------------------------------------------- #
compliance_auditor = LlmAgent(
    name="compliance_auditor",
    model=PRO_MODEL,
    description="Audits whether each agent followed its instructions and the spec; flags deviations.",
    instruction="""You audit AGENT BEHAVIOR, not code quality. Compare what each
phase was instructed to do against what it actually produced in the workspace
and in shared state ('spec', 'design_spec', 'frontend', 'backend', 'database',
'infra', 'qa_report', 'uat_report').

For each agent/phase, decide: FOLLOWED, PARTIAL, or DEVIATED, with evidence —
e.g. 'frontend_lead was told to delegate to all three specialists but only
called dataviz_engineer (no parallax/3D implemented)', or 'files written to
src/ instead of the App Router app/'. Call out skipped steps, ignored spec
items, convention violations, and unverified hand-offs.

Write 'docs/compliance-report.md' with a per-agent verdict, the concrete
deviations, and a short list of instruction/tooling changes that would prevent
them next time. Reply with the headline deviations.""",
    tools=FILE_TOOLS,
    output_key="compliance_report",
)

# --------------------------------------------------------------------------- #
# Full studio pipeline: build → refine-until-green → UAT → behavior audit.      #
# --------------------------------------------------------------------------- #
studio_pipeline = SequentialAgent(
    name="studio_pipeline",
    description="End-to-end: build the site, refine until it passes QA, UAT-and-fix in a browser until journeys pass, then audit agent behavior.",
    sub_agents=[
        website_build_pipeline,
        refinement_loop,
        uat_loop,
        compliance_auditor,
    ],
)

# --------------------------------------------------------------------------- #
# Root — conversational coordinator. Exposes the full pipeline and targeted     #
# teams as tools so the user can build end-to-end or iterate on one area.       #
# --------------------------------------------------------------------------- #
root_agent = LlmAgent(
    name="studio_director",
    model=PRO_MODEL,
    description="Coordinates a web studio of agents to design and build interactive, production-grade websites.",
    global_instruction=HOUSE_STYLE,
    instruction="""You are the studio director. Talk to the user, clarify the
brief when it is ambiguous, then deliver.
- For a new site or a full rebuild, call the `studio_pipeline` tool — it builds,
  refines until the build is green, runs browser UAT, and audits agent behavior.
- For a focused change, call the right team tool directly: `frontend_lead`
  (UI / animation / 3D / dataviz), `backend_engineer`, `database_architect`,
  `devops_engineer`, or `uat_loop` (to re-test the UI in a browser AND auto-fix
  any runtime failures until the key journeys pass).
Tool calls are SYNCHRONOUS: when `studio_pipeline` (or any team tool) returns,
the work is already COMPLETE — there is nothing left running. NEVER say you will
"monitor", "keep you posted", or report "once complete". Instead, immediately
read 'docs/qa-report.md', 'docs/uat-report.md', and 'docs/compliance-report.md'
and summarize the ACTUAL outcome: build status (pass/fail), what was built, the
top QA/UAT findings, and any agent deviations the audit flagged. Then propose a
concrete next step. Keep the user oriented; do not dump large code into chat.""",
    tools=[
        *FILE_TOOLS,  # so the director can read the report files and summarize real results
        AgentTool(agent=studio_pipeline),
        AgentTool(agent=frontend_lead),
        AgentTool(agent=backend_engineer),
        AgentTool(agent=database_architect),
        AgentTool(agent=devops_engineer),
        AgentTool(agent=uat_loop),
    ],
)

# Wire the live progress feed across the whole agent tree (director → pipeline →
# every phase/specialist). Because these are shared instances, the console
# harnesses (run_pipeline.py / run_continue.py) that recompose them inherit the
# callbacks too. See watch_progress.py to view the feed.
_register_progress_callbacks(root_agent)

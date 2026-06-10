# Workspace & Test-Run Lifecycle

How generated artifacts and completed runs are organized for this ADK studio.

## Folders

- `workspace/` — the **live** output of a single `studio_pipeline` run (frontend, backend, database,
  terraform, docs, deploy.ps1, uat/). Treated as disposable; regenerated empty at the start of each run.
- `archive/` — **snapshots** of completed runs, named `workspace-<YYYY-MM-DD>-runN[-note]`
  (e.g. `workspace-2026-06-06-run2`). Kept as showcases/reference.

## Starting a new test run

Before kicking off a new pipeline run on an existing `workspace/`, archive first:

```
/archive-workspace            # archives workspace/ -> archive/workspace-<today>-runN, resets workspace/ empty
/archive-workspace universe   # same, but suffixes the archive folder with a note
```

This excludes the regenerable/heavy dirs (`node_modules`, `.next`, `.git`, `.terraform`) and `*.tfstate`,
keeping archives to source only.

## What is committed vs ignored

Regenerable artifacts are **never** committed (see `.gitignore`): `node_modules/`, `.next/`, `.terraform/`,
`*.tfstate`, `.adk/session.db`, `__pycache__/`. Secrets live only in `.env`, which is git-ignored. The
source under `workspace/` and `archive/` (app/components, `.tf`, docs, Dockerfile, deploy.ps1) **is** kept.

## Rules Summary

| Action | Rule |
|--------|------|
| Reuse the same `workspace/` across runs without archiving | NO — run `/archive-workspace` first |
| Commit `node_modules` / `.next` / `.terraform` / `.tfstate` | NEVER (gitignored) |
| Commit `.env` or hardcode credentials | NEVER |
| Hand-author binary/media assets (`.gltf`, `.glb`, images) | NEVER — build 3D geometry procedurally |
| Run `terraform apply` from an agent | NEVER — author + `validate` only; deploy is manual via `deploy.ps1` |

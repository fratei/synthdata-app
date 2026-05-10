# SynthData Agent Framework Migration

This repository was migrated to consume the CreativeWare reusable agent framework from `fratei/creative-ware-hq`.

## What changed

- Workflows reduced from 6 to 5 by deleting redundant `.github/workflows/pr-auto-merge.yml`.
- Agent workflows now use reusable workflows:
  - `.github/workflows/observability-agent.yml`
  - `.github/workflows/pr-review.yml`
  - `.github/workflows/product-agent-fleet.yml`
- Each migrated workflow was reduced from custom inline logic to a small reusable consumer.
- `config/agents.config.json` adds SynthData-specific `high_extra_paths` for privacy/data sensitivity.
- Owner decision SLA override is set to 72h for development-stage operation.
- Agent state moved from markdown metrics to schema-based JSON files.
- Agent charters were copied from HQ (`docs/agents/charters/`).

## Framework reference and follow-up

- Framework dependency PR (link pending until available): `fratei/creative-ware-hq` — “Reusable agent framework v1: composite actions, schemas, drift detection, smoke test, HR + budget agents, prompt registry, owner inbox”.
- Since the `v1` tag is not available yet, this repo currently references `@main` placeholders.
- [ ] Switch all `uses:` references from `@main` to `@v1` once framework `v1.0.0` is tagged.

## Registry verification

`products/registry.json` in `fratei/creative-ware-hq@main` includes SynthData with `"status": "development"`.

## Smoke verification

Manual `workflow_dispatch` smoke trigger for `product-agent-fleet.yml` could not be executed from this local migration environment. Run it in GitHub Actions UI after merge to verify reusable workflow wiring.
- [ ] Post-merge: trigger `🏢 Product Agent Fleet — SynthData` and confirm successful reusable workflow run.

## Post-Phase 2 outcomes audit (2026-05-10)

- [x] Verified required files and templates are present (`.github/workflows/*`, `.github/pull_request_template.md`, `config/agents.config.json`, `docs/agents/*`, `strategy/agent-state/*.json`).
- [x] Validated baseline code quality gates locally (`cd backend && pytest tests/ -v` → passing).
- [x] Investigated GitHub Actions history and identified reusable-workflow contract drift as the primary autonomy blocker.
- [x] Fixed PR pipeline reusable workflow inputs (`owner`, `repo`) in `.github/workflows/pr-review.yml`.
- [x] Fixed product fleet reusable workflow inputs (`registry_path`) in `.github/workflows/product-agent-fleet.yml`.
- [x] Added `products/registry.json` to satisfy product fleet reusable workflow expectations.
- [ ] Manual post-merge verification: run `🔍 PR Review & Auto-Merge — SynthData` via `workflow_dispatch` and confirm successful startup.
- [ ] Manual post-merge verification: run `🏢 Product Agent Fleet — SynthData` via `workflow_dispatch` and confirm successful startup.
- [ ] Admin-only checks still required: confirm `AGENT_PAT` + deployment secrets, branch protection, and incident routing in repository settings.

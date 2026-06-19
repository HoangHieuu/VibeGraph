# VibeGraph Specification Intake

Date: 2026-06-19

## Source

- Attached repository specification: `SPEC.md`
- MCP and development tooling guidance: `MCP_SETUP.md`

## Project Summary

VibeGraph is a one-command, local-first tool for hackathon builders. It turns a
repository into a live file-level import graph, surfaces dependency warnings,
and produces graph-aware context packs and architecture documentation.

The primary user is a builder working under time pressure with AI coding tools.
Secondary users are teammates, mentors, and solo builders who need fast
architecture understanding without sending an entire repository to an LLM.

## Product Contracts Created

| File | Purpose | Source sections |
| --- | --- | --- |
| `overview.md` | Product identity, users, goals, scope | 1-9 |
| `runtime-and-cli.md` | Stack, local runtime, CLI, outputs, providers | 10-12 |
| `analysis-and-graph.md` | Scanner, parser, graph, watcher, warnings | 13-15, 17 |
| `dashboard-and-workflows.md` | UI, context pack, README, API | 16, 18-20 |
| `delivery-and-validation.md` | Phases, demo, metrics, risks, completion | 21-28 |

## Candidate Epics

| Epic | Description | Status |
| --- | --- | --- |
| E00 | Project foundation and stable output directory | selected |
| E01 | Scanner, parser, and graph JSON | unsliced |
| E02 | Interactive graph dashboard | unsliced |
| E03 | Context pack agent and offline heuristics | unsliced |
| E04 | README generation | unsliced |
| E05 | Realtime watcher and warnings | unsliced |
| E06 | npm packaging, landing page, and demo | unsliced |

## Architecture

- Runtime stack: Node CLI, Python/FastAPI backend, React/Vite frontend.
- Product surface: local browser dashboard launched from a terminal command.
- Storage: generated JSON and Markdown under `.vibegraph/`; no database in MVP.
- External provider: optional OpenRouter-compatible Gemini model.
- Deployment target: local runtime first; landing-page hosting is separate.
- Security model: source code remains local by default; only structured graph
  context is sent to the configured LLM.

## Validation Shape

| Layer | Expected proof |
| --- | --- |
| Unit | Scanner rules, import parsing, resolution, ranking, graph calculations |
| Integration | API routes, output files, watcher updates, LLM fallback behavior |
| E2E | Dashboard search, inspection, filtering, context and README workflows |
| Platform | npm CLI startup, process orchestration, browser launch, path handling |
| Release | Fresh-repo `npx` smoke test and complete demo script |

## Open Decisions

- Exact distribution strategy for shipping or acquiring the Python runtime
  through the npm package.
- Tree-sitter adoption threshold versus standard-library/fallback parsers.
- Whether the final landing page is deployed on Vercel or another static host.

## First Stories

- `US-001-local-development-foundation.md`
- `US-002-stable-output-directory.md`

## Harness Delta

- Replaced generic project surfaces with VibeGraph product contracts.
- Added architecture decisions and Phase 0 stories.
- Added planned proof rows to the test matrix.

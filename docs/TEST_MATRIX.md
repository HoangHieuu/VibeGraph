# VibeGraph Test Matrix

This file maps accepted product behavior to planned or recorded proof. A
`planned` row is not an implementation claim.

## Status Values

| Status | Meaning |
| --- | --- |
| planned | Accepted behavior, not implemented |
| in_progress | Actively being built |
| implemented | Implemented and proof exists |
| changed | Contract changed after earlier implementation |
| retired | No longer part of the product contract |

## Selected Story Matrix

| Story | Contract | Unit | Integration | E2E | Platform | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US-001 | Developer starts frontend/backend and sees healthy connection without an API key | yes | yes | yes | yes | implemented | `pnpm check`; browser QA at 1280x720 and 390x844 |
| US-002 | Backend creates a safe, idempotent `.vibegraph/` output boundary | yes | yes | no | yes | implemented | `pnpm check`; E2E not required; live startup created an empty root output directory |
| US-101 | Local CLI scans supported source files and publishes a directed graph artifact/API | yes | yes | yes | yes | implemented | `pnpm check`; 41-file live scan with 110 links and 0 warnings; built CLI launched dashboard/API on port 8732 |
| US-201 | Dashboard provides interactive graph exploration, degree-scaled dot rendering, direct-neighborhood hover highlighting, readable topology, inspection, search, filters, and grouping | yes | yes | yes | yes | implemented | `pnpm check`; highlight-set unit tests; in-app browser QA confirmed immediate neighbor/edge highlighting, relevant labels, unrelated-element dimming, search focus, and clean console |
| US-301 | Context packs rank graph files offline, optionally enhance wording through OpenRouter, write `.vibegraph/context.md`, and support prompt/mention copying | yes | yes | yes | yes | implemented | `pnpm check`; 19 backend, 8 CLI, and 16 frontend tests; live offline and DeepSeek-enhanced browser QA; provider fallback and metadata-only request proof |
| US-401 | README generation derives modules, commands, key files, and bounded Mermaid output from graph data with offline/provider fallback | yes | yes | yes | yes | implemented | `pnpm check`; 25 backend, 8 CLI, and 19 frontend tests; offline desktop/mobile browser QA; live DeepSeek enhancement in 6.83 seconds; metadata-only provider payload proof |
| US-501 | Supported file changes trigger debounced graph rebuilds, typed warning artifacts, WebSocket updates, and dashboard warning visuals | yes | yes | yes | yes | implemented | `pnpm check`; 29 backend, 8 CLI, and 21 frontend tests; story verification passed; live missing-symbol warning in 0.819 seconds; browser warning creation/resolution and clean console proof |
| US-601 | Packed npm CLI bundles the dashboard/backend, bootstraps isolated Python, and launches outside the monorepo | yes | yes | yes | yes | in_progress | `pnpm check`; `pnpm package`; fresh tarball install and launch passed on macOS with 2-file graph; Ubuntu CI passed remotely; Windows path-test and smoke portability fixes pass locally, with the next remote Windows run and public registry publication still pending |

## Future Validation Map

| Epic | Required proof focus |
| --- | --- |
| E01 Scanner and graph | Parser/unit fixtures, mixed-language integration repositories, graph JSON schema |
| E02 Dashboard | Component behavior, browser E2E, 100-node interaction check |
| E03 Context packs | Ranking unit tests, offline/provider integration, graph-query assertion |
| E04 README | Deterministic formatting, Mermaid validity, provider fallback |
| E05 Watcher | Filesystem integration, WebSocket E2E, warning latency |
| E06 Packaging and demo | Fresh-environment `npx`, platform smoke tests, complete demo run |

## Evidence Rules

- Unit proof covers pure domain and application rules.
- Integration proof covers backend, filesystem, provider, watcher, and service
  contracts.
- E2E proof covers visible browser workflows.
- Platform proof covers CLI, process, path, browser-open, and packaging
  behavior not proven at lower layers.
- Story packets may omit a proof layer only when they explain why.

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
| US-002 | Backend creates a safe, idempotent `.vibegraph/` output boundary | no | no | no | no | planned | none |

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

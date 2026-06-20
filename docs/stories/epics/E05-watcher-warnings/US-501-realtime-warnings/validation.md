# Validation

## Proof Strategy

Prove warning derivation as pure graph comparison, then prove filesystem
debounce and WebSocket delivery with temporary repositories. Browser proof
modifies and restores a demo dependency while the dashboard is open.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Missing symbols, deleted files, new orphans, new cycles |
| Integration | Debounced file save, artifacts, WebSocket event |
| E2E | Break dependency, observe console/node/edge update, restore |
| Platform | Watchdog startup/shutdown and Vite WebSocket proxy |
| Performance | Warning visible within two seconds after save |
| Logs/Audit | Ignored and unsupported events do not trigger scans |

## Fixtures

- Temporary Python import graph with exported symbols.
- Temporary TypeScript graph with a removable local dependency.
- Small directed cycle fixture.

## Commands

```text
pnpm check
scripts/bin/harness-cli story verify US-501
```

## Acceptance Evidence

- Warning-domain tests cover missing exported symbols, deleted imported files,
  newly orphaned files, and newly introduced directed cycles.
- Filesystem integration uses Watchdog's cross-platform polling observer and
  proves supported-file filtering plus event coalescing under debounce.
- FastAPI integration proves `graph_updated` and `warning_created` WebSocket
  payloads and `.vibegraph/warnings.json` persistence.
- Frontend boundary and component tests prove parsed realtime events and
  actionable warning-console rendering.
- A real repository scan excludes `backend/.uv-cache` and produced 66 files,
  233 links, and zero false warnings.
- In-app browser QA changed `validate_session` to an invalid export and
  observed the warning console, red nodes, and broken edge update without
  restart. Restoring the symbol cleared all warning state.
- File timestamp to warning timestamp measured 0.819 seconds, below the
  two-second target.
- Browser console warnings/errors were empty during the live interaction.
- `scripts/bin/harness-cli story verify US-501` passed with 29 backend, 8 CLI,
  and 21 frontend tests plus typechecks and production builds.

# US-002 Stable Output Directory

## Status

implemented

## Lane

normal

## Product Contract

VibeGraph creates and owns a predictable `.vibegraph/` directory inside the
analyzed project without allowing generated artifacts to re-enter scans.

## Relevant Product Docs

- `docs/product/runtime-and-cli.md`
- `docs/product/analysis-and-graph.md`
- `docs/ARCHITECTURE.md`

## Acceptance Criteria

- A backend filesystem service creates `.vibegraph/` when absent.
- Creation is idempotent.
- The four required artifact paths are represented by one shared configuration
  or value object.
- The scanner ignore configuration reserves `.vibegraph/`.
- No artifact file needs to exist before its producing feature runs.
- Filesystem errors return actionable messages without exposing API keys.
- Tests use temporary project directories and do not write generated artifacts
  into this repository.

## Design Notes

- Commands: output initialization is invoked by backend startup or scan setup.
- API: no public endpoint is required in this story.
- Domain rules: generated paths are project-root-relative and cannot escape the
  selected project root.
- UI surfaces: none.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | Required path calculation and ignore rule |
| Integration | Creation, idempotency, and filesystem failure behavior |
| E2E | Not required |
| Platform | Temporary-directory behavior on supported development platforms |
| Release | Not required |

## Harness Delta

- Add the eventual output-service test command as story verification.

## Evidence

- `pnpm check`
  - Backend: 6 tests passed.
  - CLI: 3 tests passed.
  - Frontend: 2 tests passed.
  - Typechecks and production builds passed.
- Backend startup created `.vibegraph/` at the selected project root.
- The initialized directory was empty; no placeholder artifact files were
  created.
- Unit proof covers all four reserved artifact paths and the shared scanner
  ignore rule.
- Integration proof covers idempotent creation and actionable failure when
  `.vibegraph` conflicts with an existing file.
- Browser smoke confirmed the existing dashboard remained connected with no
  console warnings or errors.

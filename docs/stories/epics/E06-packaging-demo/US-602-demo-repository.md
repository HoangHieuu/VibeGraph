# US-602 Demo Repository

## Status

implemented

## Lane

normal

## Product Contract

VibeGraph includes a compact FastAPI and React repository whose authentication
flow demonstrates graph exploration, broken-symbol warnings, context-pack
ranking, and README generation within five minutes.

## Relevant Product Docs

- `docs/product/delivery-and-validation.md`
- `docs/product/analysis-and-graph.md`
- `docs/product/dashboard-and-workflows.md`

## Acceptance Criteria

- The sample lives under `demo/` and contains FastAPI, React, tests, and simple
  agent-tool modules.
- The auth route imports `validate_session` from a dedicated session service.
- A documented break/restore flow renames that symbol and produces a
  VibeGraph missing-symbol warning.
- The recommended context for the auth-fix task includes the route, session
  service, error model, and relevant test.
- The demo project can be installed, tested, and built independently.

## Design Notes

- Commands: `pnpm demo:check`, `pnpm demo:break`, `pnpm demo:restore`
- UI surfaces: sign-in form, session result, agent activity
- Domain rules: demo credentials are local fixtures and not production auth

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | Session validation and frontend typecheck |
| Integration | FastAPI auth endpoint tests |
| E2E | VibeGraph scans and ranks the auth neighborhood |
| Platform | Break/restore scripts are cross-platform Node scripts |
| Release | Five-minute demo run |

## Harness Delta

The demo is a release fixture and should remain intentionally small.

## Evidence

- `pnpm demo:check` passed with two backend integration tests and the production
  frontend build.
- Live VibeGraph scan produced 18 source files, 27 links, three languages, and
  zero baseline warnings.
- `pnpm demo:break` produced a typed `MISSING_EXPORTED_SYMBOL` warning for
  `validate_session`; `pnpm demo:restore` cleared the intentional source change.
- Offline context generation included the auth route, session service, error
  model, and auth-flow test, and wrote `.vibegraph/context.md`.
- Offline README generation wrote `.vibegraph/README.generated.md`.

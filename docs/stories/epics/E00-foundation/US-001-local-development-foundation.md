# US-001 Local Development Foundation

## Status

implemented

## Lane

normal

## Product Contract

A developer can start the backend and frontend locally, observe a successful
frontend-to-backend health request, and do so without an LLM API key.

## Relevant Product Docs

- `docs/product/runtime-and-cli.md`
- `docs/product/dashboard-and-workflows.md`
- `docs/product/delivery-and-validation.md`
- `docs/ARCHITECTURE.md`

## Acceptance Criteria

- The repository has clear `frontend`, `backend`, and `cli` workspaces.
- The backend starts locally and exposes `GET /api/health`.
- The frontend starts locally and displays backend health state.
- The CLI workspace has a typed command entrypoint, even if full orchestration
  is deferred to a later story.
- One documented development command starts the required local services.
- Startup succeeds with no LLM API key.
- README contains current local development instructions after implementation.

## Design Notes

- Commands: select root workspace scripts during implementation.
- Queries: `GET /api/health`.
- API: health response must be small, typed, and stable enough for smoke proof.
- Domain rules: no product analysis behavior is introduced in this story.
- UI surfaces: minimal dashboard shell and health indicator only.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | CLI argument/config parsing only if introduced |
| Integration | Backend health route and frontend API client |
| E2E | Local page loads and shows healthy backend |
| Platform | Development commands start on macOS; commands are portable by design |
| Release | Not required; `npx` packaging belongs to E06 |

## Harness Delta

- Replace placeholder development guidance with executable commands.
- Add selected stack commands to the story verification field.

## Evidence

- `pnpm check`
  - Backend: 1 test passed.
  - CLI: 3 tests passed.
  - Frontend: 2 tests passed.
  - CLI and frontend typechecks passed.
  - CLI and frontend production builds passed.
- `pnpm dev`
  - FastAPI served `http://127.0.0.1:8000/api/health`.
  - Vite served `http://127.0.0.1:5173`.
  - The frontend displayed `Backend connected` through the Vite API proxy.
- In-app browser verification:
  - Desktop viewport: 1280x720.
  - Mobile viewport: 390x844 with no horizontal overflow.
  - `Check again` triggered a second successful health request.
  - No application console warnings or errors.
- CLI smoke:
  - `node cli/dist/index.js . --port 9000 --no-open`.

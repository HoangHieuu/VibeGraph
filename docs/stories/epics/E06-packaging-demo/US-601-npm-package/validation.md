# Validation

## Proof Strategy

Prove deterministic path and command construction in unit tests, production
static serving in backend integration tests, package contents with `npm pack`,
and the complete launch from a temporary project outside the monorepo.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Runtime asset discovery, cache path, Python environment paths |
| Integration | FastAPI serves production index/assets while APIs remain available |
| E2E | Packed CLI launches a temporary repository and renders its graph |
| Platform | Tarball install, Python discovery, first-run bootstrap, signal shutdown |
| Performance | First graph remains below the 30-second demo target after bootstrap |
| Logs/Audit | Clear startup output; no key or source-content logging |

## Fixtures

- Temporary source repository containing a small Python module graph.
- Production frontend built from `frontend/`.
- npm tarball assembled from `cli/`.
- Isolated temporary runtime cache.

## Commands

```text
pnpm check
pnpm package
pnpm test:package
scripts/bin/harness-cli story verify US-601
```

## Acceptance Evidence

- `pnpm check` passed with 31 backend, 12 CLI, and 21 frontend tests plus
  production builds.
- `pnpm package` produces the scoped `@vibedev/vibegraph` npm tarball under
  `dist/`.
- npm dry-run inspection reported 35 package entries, 145824 compressed bytes,
  and 482143 unpacked bytes, including the CLI, backend, and frontend.
- `pnpm test:package` installed the tarball into a temporary npm project,
  created a fresh isolated Python environment, scanned a separate two-file
  repository, served health/graph/frontend endpoints, wrote
  `.vibegraph/graph.json`, and shut down cleanly. The verified first graph took
  9588 ms, below the 30-second target.
- A second packaged launch reused the cached Python environment.
- In-app browser QA on the packaged runtime at port 8844 rendered one graph
  canvas, found and opened `backend/app/main.py`, showed no error overlay, and
  produced no console warnings or errors.
- Generated runtime assets live under `cli/dist/`, so scanning the VibeGraph
  repository does not add duplicate package-source nodes.
- Public npm publication and Windows/Linux smoke proof remain open, so the
  story stays `in_progress`. The owner selected `@vibedev/vibegraph`, visible
  author `vibedev`, and the MIT license.

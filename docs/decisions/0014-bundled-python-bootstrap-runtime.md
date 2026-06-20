# 0014 Bundled Python Bootstrap Runtime

Date: 2026-06-20

## Status

Accepted

## Context

The npm CLI must launch the implemented Python backend and React dashboard
outside the development monorepo. Requiring `pnpm`, `uv`, or a separately
started backend would violate the one-command product experience. Rewriting the
backend or producing native executables would substantially expand Phase 6.

## Decision

The npm artifact bundles:

- The compiled Node CLI.
- The installable Python backend source and dependency manifest.
- The production frontend assets.

The Node CLI requires Node.js 22+ and Python 3.11+. On first packaged launch it
creates a versioned virtual environment in the user's VibeGraph cache, installs
the bundled Python project with `pip`, and reuses that environment until the
dependency manifest changes.

The packaged backend serves the frontend and API from one localhost port. The
development checkout keeps its existing `pnpm dev` fallback.

The registry package name remains a publication-time concern because the
unscoped `vibegraph` name is already occupied by an unrelated package. This
decision preserves the `vibegraph` executable without claiming registry-name
ownership.

## Alternatives Considered

1. Bundle a PyInstaller-style executable for every platform. Deferred because
   it requires a native release matrix and much larger artifacts.
2. Require `uv` and execute the source directly. Rejected because `uv` is not a
   standard npm-user prerequisite.
3. Install dependencies into the user's global Python. Rejected because it can
   conflict with user environments and is difficult to remove safely.
4. Start two development servers from the package. Rejected because it ships
   unnecessary frontend tooling and creates avoidable port/process complexity.

## Consequences

Positive:

- The complete implemented backend ships without a rewrite.
- The dashboard and API use one local origin and one public port.
- Repeated launches avoid repeated dependency installation.
- The analyzed repository contains only documented `.vibegraph/` artifacts.

Tradeoffs:

- Python 3.11+ remains a prerequisite.
- First launch needs package-index access and takes longer.
- Cross-platform cache, Python discovery, and process shutdown require explicit
  release tests.
- Public npm naming must be resolved before registry publication.

## Follow-Up

- Add platform smoke proof for macOS, Linux, and Windows.
- Resolve and document the public registry package name before publication.
- Reconsider prebuilt native backends if Python bootstrap materially harms the
  demo or adoption experience.

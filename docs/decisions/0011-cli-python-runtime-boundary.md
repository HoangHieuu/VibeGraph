# 0011 CLI and Python Runtime Boundary

Date: 2026-06-19

## Status

Accepted

## Context

The public command is an npm executable, while analysis and API behavior are
implemented in Python. The boundary must be fixed before choosing a packaging
mechanism.

## Decision

The Node CLI owns:

- Argument and project-path validation.
- Port and browser-open options.
- Python backend process startup and shutdown.
- Health readiness and terminal output.

The Python backend owns all product analysis, watching, API, WebSocket, and
artifact-writing behavior.

The exact release distribution mechanism for Python is deliberately deferred.
Phase 0 must support a documented development runtime, and Phase 6 must prove
the fresh-environment `npx` experience.

## Alternatives Considered

1. Duplicate scanner logic in the Node CLI.
2. Make the Python service a manually launched prerequisite.
3. Decide packaging before a working local vertical slice exists.

## Consequences

Positive:

- Responsibility is stable while packaging remains reversible.
- Development can start without pretending the hardest release problem is
  solved.

Tradeoffs:

- Phase 0 and Phase 6 have different startup proof.
- Process lifecycle and cross-platform behavior need platform tests.

## Follow-Up

- Record the distribution mechanism in a new decision before npm release.

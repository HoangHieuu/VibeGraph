# 0009 Local-First and Offline-Capable Runtime

Date: 2026-06-19

## Status

Accepted

## Context

Hackathon users need low setup cost and may not have an API key or reliable
provider access. Repository source can also be sensitive.

## Decision

Core VibeGraph behavior runs locally without an API key:

- Scanning and graph generation.
- Dashboard and file inspection.
- Watching and warnings.
- Deterministic context recommendation.
- Structured README generation.

OpenRouter-compatible Gemini calls may enhance explanations and prose. They
must consume structured graph context, fail closed to deterministic behavior,
and never become a startup requirement.

## Alternatives Considered

1. Require an LLM key for every context or README workflow.
2. Upload repositories to a hosted analysis service.
3. Disable context and README features in offline mode.

## Consequences

Positive:

- The product remains demoable and useful with minimal setup.
- Repository analysis stays local by default.
- Provider outages do not remove core workflows.

Tradeoffs:

- Deterministic ranking and prose require first-class implementation and tests.
- Provider and fallback paths must remain behaviorally consistent.

## Follow-Up

- Add explicit provider-failure integration tests in the context and README
  stories.

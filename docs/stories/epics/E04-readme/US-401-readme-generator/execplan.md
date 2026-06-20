# Exec Plan

## Goal

Deliver a graph-derived README workflow that is complete offline and can
optionally improve prose through `deepseek/deepseek-v4-flash`.

## Scope

In scope:

- Deterministic README sections and local metadata inspection.
- Bounded, graph-derived Mermaid output.
- `POST /api/readme`.
- `.vibegraph/README.generated.md`.
- OpenRouter prose enhancement and deterministic fallback.
- Dashboard generation, preview, artifact confirmation, and copy action.

Out of scope:

- Sending source contents to a provider.
- Overwriting repository documentation.
- Provider-controlled graph or command generation.
- Watcher and realtime warning work from Phase 5.

## Risk Classification

Risk flags:

- External systems.
- Public contracts.
- Existing behavior.
- Weak proof until fallback and privacy tests exist.

Hard gate:

- External provider behavior.

## Work Phases

1. Story and validation contract.
2. Deterministic backend generation.
3. Provider enhancement and fallback.
4. Dashboard workflow.
5. Automated and browser verification.
6. Durable evidence and Harness trace.

## Stop Conditions

Pause for human confirmation if:

- Source content would need to leave the local machine.
- Provider output must control file selection, commands, or Mermaid edges.
- The existing repository README would need to be overwritten.
- Validation requirements need to be weakened.

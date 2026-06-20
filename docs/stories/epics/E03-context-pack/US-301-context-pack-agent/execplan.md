# Exec Plan

## Goal

Deliver a graph-aware context-pack workflow that remains fully usable offline
and optionally improves wording through OpenRouter using
`deepseek/deepseek-v4-flash`.

## Scope

In scope:

- Deterministic graph ranking with bounded depth and file count.
- `POST /api/context-pack`.
- `.vibegraph/context.md`.
- OpenRouter enhancement from structured graph metadata.
- Provider failure fallback.
- Dashboard task input, results, copy prompt, and copy mentions.

Out of scope:

- Sending source file contents to a provider.
- Editing repository source.
- README generation.
- Provider routing beyond the configured OpenRouter model.

## Risk Classification

Risk flags:

- External systems.
- Public contracts.
- Existing behavior.
- Weak proof until provider fallback tests exist.

Hard gates:

- External provider behavior.

## Work Phases

1. Discovery.
2. Design.
3. Validation planning.
4. Implementation.
5. Verification.
6. Harness update.

## Stop Conditions

Pause for human confirmation if:

- Source content would need to leave the local machine.
- Provider configuration needs credentials stored in generated artifacts.
- The API response contract must materially diverge from the product docs.
- Validation requirements need to be weakened.

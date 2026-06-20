# 0012 OpenRouter DeepSeek Prose Model

Date: 2026-06-19

## Status

Accepted

## Context

The original product contract recommended a Gemini model for optional context
wording enhancement. The selected project configuration now uses OpenRouter
model `deepseek/deepseek-v4-flash`.

## Decision

Use `VIBEGRAPH_MODEL=deepseek/deepseek-v4-flash` as the project default for
OpenRouter context-pack and generated-README prose enhancement.

For context packs, the provider receives only the task and structured metadata
for files already selected by deterministic graph ranking. For README
generation, it receives project statistics, deterministic modules, entry
points, key files, commands, warnings, and bounded graph relationships. It does
not receive source contents or absolute project paths and cannot change file
selection, commands, warnings, or Mermaid edges.

Missing keys, request failures, invalid responses, and model failures fall back
to deterministic output. Provider enhancement is bounded at 25 seconds because
live DeepSeek completion latency can exceed deterministic generation targets.

## Alternatives Considered

1. Keep the original Gemini recommendation.
2. Let the provider choose and rank repository files.
3. Send complete selected file contents for richer prose.

## Consequences

Positive:

- Matches the configured model selected by the project owner.
- Keeps provider behavior replaceable through `VIBEGRAPH_MODEL`.
- Preserves local-first privacy and deterministic structural analysis.

Tradeoffs:

- Provider-specific output quality can vary.
- Enhancement needs strict parsing and fallback tests.

## Follow-Up

- Revalidate the model identifier before release packaging.

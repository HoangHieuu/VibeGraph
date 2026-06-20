# Design

## Domain Model

- `ContextPackRequest`: task and bounded ranking options.
- `ContextRecommendation`: path, deterministic score, and reason.
- `ContextPack`: mode, model, recommendations, prompt, mentions, estimates,
  provider status, and artifact path.
- `ContextEnhancement`: provider-returned rationale, prompt, and optional
  per-file reason overrides.

Rules:

- Graph retrieval and ranking always run before provider enhancement.
- Maximum file count is clamped to 1-20 and depth to 0-4.
- Unknown/external nodes are excluded from recommendations.
- Source contents are not part of provider input.

## Application Flow

```text
task
  -> parse request
  -> tokenize task and identify seed files
  -> traverse graph within max depth
  -> score and rank candidates
  -> build deterministic pack
  -> optionally request OpenRouter wording enhancement
  -> validate enhancement or fall back
  -> write .vibegraph/context.md
  -> return parsed response
```

## Interface Contract

```text
POST /api/context-pack
```

Request fields:

- `task`
- `maxFiles`
- `maxDepth`
- `includeTests`
- `includeConfig`
- `includeDocs`

Response fields:

- `task`
- `mode`
- `model`
- `recommendations`
- `prompt`
- `mentions`
- `estimatedTokens`
- `reductionPercent`
- `providerMessage`
- `artifactPath`

Invalid tasks return HTTP 422. Provider failures do not change the HTTP success
contract when deterministic generation succeeds.

## Data Model

No database changes. The backend remains the sole writer of
`.vibegraph/context.md`.

## UI / Platform Impact

The dashboard adds a context-pack panel with task input, generation state,
offline/enhanced status, recommendations, estimates, and copy actions.

The backend reads `OPENROUTER_API_KEY` and `VIBEGRAPH_MODEL` from process
environment. Development loads the repository `.env` through Uvicorn.

## Observability

Provider status is explicit in the response:

- `offline`
- `enhanced`
- `fallback`

API keys and provider request bodies are not logged or written to artifacts.
Provider calls use a bounded 25-second timeout before deterministic fallback.

## Alternatives Considered

1. Send complete selected files to OpenRouter. Rejected for privacy and scope.
2. Require OpenRouter for every result. Rejected by offline-first decision.
3. Use provider output to choose files. Rejected because graph retrieval must
   remain authoritative and testable.

# Validation

## Proof Strategy

Prove deterministic ranking independently, then prove provider enhancement and
failure fallback with fake clients. Browser proof covers the complete task,
result, and copy workflow.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Task matching, depth, filters, ranking, estimates, markdown |
| Integration | API success, artifact writing, provider enhancement/failure |
| E2E | Submit task, inspect recommendations, copy prompt and mentions |
| Platform | No-key startup and configured-key development runtime |
| Performance | Ranking remains bounded by graph size and configured limits |
| Logs/Audit | No key or source contents in response/artifact |

## Fixtures

- Mixed Python/TypeScript graph fixture.
- Fake successful OpenRouter client.
- Fake failing OpenRouter client.
- Malformed provider response.

## Commands

```text
pnpm check
scripts/bin/harness-cli story verify US-301
```

## Acceptance Evidence

- Deterministic ranking tests cover explicit target matching, direct graph
  neighbors, tests, filters, bounded selection, estimates, and markdown output.
- Provider tests prove enhancement cannot change the selected file set,
  malformed/failing provider behavior falls back, and outbound payloads contain
  graph metadata without source contents or absolute project paths.
- Live OpenRouter verification used `deepseek/deepseek-v4-flash` and returned
  schema-constrained enhanced reasons and prompt wording. Measured live latency
  was approximately 22 seconds, within the optional 25-second provider bound.
- In-app browser QA verified offline and enhanced modes, saved artifact status,
  ranking order, prompt copying, file-mention copying, and clean console output.
- `pnpm check` passed with 19 backend, 8 CLI, and 16 frontend tests.

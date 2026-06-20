# Validation

## Proof Strategy

Prove deterministic selection and rendering independently, then prove provider
enhancement and failure fallback with fake clients. Browser proof covers the
complete dashboard workflow.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Module ranking, key files, commands, Mermaid IDs/edges, Markdown |
| Integration | API success, artifact writing, enhancement and fallback |
| E2E | Generate, inspect status and preview, copy Markdown |
| Platform | No-key and configured-key local runtime |
| Performance | Generation completes within the 15-second offline target |
| Privacy | Provider payload excludes source content and absolute paths |

## Commands

```text
pnpm check
scripts/bin/harness-cli story verify US-401
```

## Acceptance Evidence

- Deterministic tests cover graph-derived modules, conventional entry points,
  bounded key-file selection, local package commands, unresolved-import
  warnings, Mermaid nodes/edges, Markdown sections, and artifact writing.
- Provider tests prove enhanced prose cannot alter key files, commands, or
  Mermaid output; provider failure preserves the deterministic artifact.
- Provider payload tests prove source contents and absolute project paths are
  excluded.
- Live OpenRouter verification used `deepseek/deepseek-v4-flash`, returned
  enhanced prose in 6.83 seconds, and preserved three deterministic modules,
  ten key files, commands, warnings, and Mermaid structure.
- In-app browser QA at 1280x720 and 390x844 verified panel access, optional
  description input, offline generation, artifact confirmation, Markdown
  preview, clipboard content, mobile access, and clean console output.
- `pnpm check` passed with 25 backend, 8 CLI, and 19 frontend tests.

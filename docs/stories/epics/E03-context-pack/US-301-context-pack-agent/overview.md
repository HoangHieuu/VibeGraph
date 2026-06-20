# Overview

## Current Behavior

The dashboard exposes placeholder context-pack actions. The backend has graph
data and reserves `.vibegraph/context.md`, but no ranking, API, provider, or
artifact workflow exists.

## Target Behavior

A builder submits a natural-language coding task and receives up to eight
ranked files, reasons, a prompt, file mentions, estimated context size, and
reduction percentage. The result is written to `.vibegraph/context.md`.

Without an API key, the result is deterministic. With an OpenRouter key, the
configured model may improve reasons and prompt wording using structured graph
metadata only. Provider failure returns the deterministic result.

## Affected Users

- Hackathon builder using an AI coding tool.
- Solo builder minimizing context-window usage.
- Teammate investigating an unfamiliar repository.

## Affected Product Docs

- `docs/product/dashboard-and-workflows.md`
- `docs/product/runtime-and-cli.md`
- `docs/product/delivery-and-validation.md`

## Non-Goals

- Code generation or source modification.
- Full semantic retrieval.
- Uploading whole files or repository archives.
- README generation.

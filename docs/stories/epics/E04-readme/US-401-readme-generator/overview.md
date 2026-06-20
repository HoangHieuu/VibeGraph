# Overview

## Current Behavior

The dashboard exposes a placeholder “Generate README” action. The backend
reserves `.vibegraph/README.generated.md`, but no generator, API, provider
enhancement, or artifact workflow exists.

## Target Behavior

A builder generates a submission-ready README draft from the current graph.
The output contains deterministic project statistics, entry points, main
modules, run commands, key files, warnings, and a bounded Mermaid diagram.

Without an API key, the complete structured README remains available. With an
OpenRouter key, the configured model may improve overview, architecture, and
module-description prose using structured graph metadata only. Provider
failure preserves the deterministic result.

## Affected Users

- Hackathon builders preparing a submission.
- Solo builders documenting an unfamiliar codebase quickly.
- Judges, mentors, and teammates reviewing project architecture.

## Affected Product Docs

- `docs/product/dashboard-and-workflows.md`
- `docs/product/runtime-and-cli.md`
- `docs/product/delivery-and-validation.md`

## Non-Goals

- Replacing or modifying the repository’s existing `README.md`.
- Sending source file contents to an external provider.
- Allowing provider output to select files, commands, or graph edges.
- Generating warnings beyond the current graph’s unresolved imports.

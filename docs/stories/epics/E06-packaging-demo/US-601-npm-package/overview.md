# Overview

## Current Behavior

The TypeScript CLI only works from the VibeGraph monorepo. It starts
`pnpm dev`, so an installed npm package would not contain or launch the Python
backend and built dashboard.

## Target Behavior

The CLI can be packed as an npm tarball containing its compiled JavaScript, the
Python backend source, and the production frontend. On first launch it creates
an isolated cached Python environment, installs the bundled backend and its
locked runtime dependencies, then serves the API and dashboard from one local
port.

## Affected Users

- Builders launching VibeGraph from npm or an npm tarball.
- Judges evaluating the one-command local-first experience.
- Maintainers publishing and smoke-testing release artifacts.

## Affected Product Docs

- `docs/product/runtime-and-cli.md`
- `docs/product/delivery-and-validation.md`

## Non-Goals

- Publishing to the npm registry in this story.
- Removing the Python 3.11+ prerequisite.
- Landing-page implementation.
- Demo-video or Devpost submission production.
- Supporting the unrelated existing `vibegraph` npm package.

# 0015 Scoped npm Release Identity

Date: 2026-06-20

## Status

Accepted

## Context

The product specification used `npx vibegraph@latest .`, but the unscoped
`vibegraph` registry name is owned by an unrelated project. Phase 6 needs an
owned package identity, author metadata, repository links, and a license before
publication.

## Decision

Publish the CLI as:

```text
@vibedev/vibegraph
```

The package continues to expose the `vibegraph` executable, so global or local
install users retain the short command. The public one-shot command is:

```bash
npx @vibedev/vibegraph@latest .
```

Release metadata:

- Visible author: vibedev
- Repository: `https://github.com/HoangHieuu/VibeGraph`
- License: MIT

## Alternatives Considered

1. Use the occupied unscoped name. Rejected because it cannot represent this
   project.
2. Choose another unscoped brand variant. Rejected because the npm username
   already provides a stable namespace without changing the product name.
3. Rename the executable to match the scoped package. Rejected because npm
   package scope does not require changing the user-facing binary.

## Consequences

Positive:

- Registry identity is explicit and collision-free.
- The package links directly to the canonical repository and issue tracker.
- The established `vibegraph` terminal command remains available.

Tradeoffs:

- The one-shot `npx` command is longer than the original specification.
- Publishing requires npm access to the `vibedev` scope.

## Follow-Up

- Confirm `vibedev` npm authentication and publish access.
- Update landing-page and demo copy to use the scoped command.

# Design

## Registry Contract

```text
package: @vibedev/vibegraph
version: 0.1.0
access: public
tag: latest
binary: vibegraph
```

## Security Boundary

Authentication remains in the user's npm configuration. Tokens must not be
written to the repository, logs, Harness database, or generated artifacts.

## Rollback

npm versions are immutable. If the release is incorrect, deprecate it and
publish a corrected patch version rather than overwriting `0.1.0`.

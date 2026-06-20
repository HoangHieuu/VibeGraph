# Exec Plan

## Goal

Publish the already validated `@hoanghieudev/vibegraph@0.1.0` artifact.

## Risk Classification

- External registry mutation.
- Public installation contract.
- Package-scope ownership and authentication.

## Work Phases

1. Confirm `npm whoami` returns `hoanghieudev`.
2. Run `npm publish --dry-run --access public`.
3. Publish from `cli/`.
4. Verify registry metadata and a fresh `npx` launch.
5. Record the release URL and proof.

## Stop Conditions

Stop before publication when npm authentication or scope ownership is absent.

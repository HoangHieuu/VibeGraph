# Overview

## Current Behavior

The scoped npm artifact is published publicly as
`@hoanghieudev/vibegraph@0.1.0`.

## Target Behavior

Version `0.1.0` is published publicly under the authenticated `hoanghieudev`
npm scope and the documented `npx @hoanghieudev/vibegraph@latest .` command
resolves.

## Affected Users

- Builders installing VibeGraph.
- Judges validating the one-command launch.
- Maintainers publishing releases.

## Non-Goals

- Automated npm trusted publishing.
- Semantic-release automation.
- Changing the package name or version.

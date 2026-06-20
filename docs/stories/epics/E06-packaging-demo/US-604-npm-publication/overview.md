# Overview

## Current Behavior

The scoped npm artifact is fully packaged and validated locally and on Ubuntu,
Windows, and macOS, but `@vibedev/vibegraph` is not published.

## Target Behavior

Version `0.1.0` is published publicly under the authenticated `vibedev` npm
scope and the documented `npx @vibedev/vibegraph@latest .` command resolves.

## Affected Users

- Builders installing VibeGraph.
- Judges validating the one-command launch.
- Maintainers publishing releases.

## Non-Goals

- Automated npm trusted publishing.
- Semantic-release automation.
- Changing the package name or version.

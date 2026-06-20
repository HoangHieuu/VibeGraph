# Exec Plan

## Goal

Produce and validate an installable npm artifact that launches the complete
VibeGraph dashboard and backend outside the monorepo.

## Scope

In scope:

- Bundle compiled CLI, backend source, and production frontend.
- Bootstrap an isolated cached Python environment.
- Serve production frontend and APIs from one process and port.
- Preserve local monorepo development behavior.
- Prove installation and launch from a packed tarball.

Out of scope:

- npm registry publication.
- Claiming the unavailable unscoped `vibegraph` npm name.
- Landing page, demo repository, video, and submission copy.
- Native Python-free executables.

## Risk Classification

Risk flags:

- Public CLI contract.
- Existing startup behavior.
- Cross-platform process and filesystem behavior.
- External package indexes during first-run dependency installation.
- Weak release proof until a packed artifact runs outside the workspace.

Hard gates:

- External system behavior.
- Public installation contract.

## Work Phases

1. Record packaging and runtime distribution decision.
2. Add package assembly and Python project metadata.
3. Add packaged runtime bootstrap and production static serving.
4. Add unit and integration coverage.
5. Pack, install, launch, and browser-test the artifact.
6. Update product docs, matrix proof, and Harness records.

## Stop Conditions

Pause for human confirmation if:

- Publishing requires credentials or ownership changes.
- The product must remove the Python prerequisite.
- Validation would require source-code upload or weaker privacy guarantees.
- The public package name must change in living product contracts.

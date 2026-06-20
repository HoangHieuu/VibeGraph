# Product Overview

## Identity

Product: **VibeGraph**

Tagline: **Live codebase maps for AI-powered builders.**

VibeGraph converts a local repository into a live, Obsidian-like code graph and
recommends the exact files a builder should provide to an AI coding tool.

## Users

The primary user is a hackathon builder who is changing code quickly, using AI
coding tools heavily, and collaborating under deadline pressure.

Secondary users:

- A teammate joining a repository mid-event.
- A mentor inspecting architecture before giving advice.
- A solo builder minimizing context-window usage.

## Problems

VibeGraph addresses:

1. Architecture drift as imports and modules change.
2. Context overload when builders cannot identify the minimal relevant files.
3. Submission friction when architecture and README documentation are delayed
   until demo time.

## Product Promise

A builder can:

1. Run `npx @hoanghieudev/vibegraph@latest .`.
2. View the repository as a live file-level import graph.
3. Inspect a file and its dependencies.
4. request a graph-aware context pack for a coding task.
5. Save generated artifacts under `.vibegraph/`.
6. Receive near-realtime warnings when local dependencies break.

## Goals

- One-command local launch.
- Python, JavaScript, and TypeScript file-level import analysis.
- Interactive graph exploration.
- Minimal context recommendations with deterministic offline behavior.
- Broken dependency warnings.
- Submission-ready README generation.

## Non-Goals

The MVP does not provide:

- Function-level call graphs.
- Full semantic code understanding or production static analysis.
- Automatic source-code modification.
- An IDE extension.
- Cloud repository ingestion or multi-user collaboration.
- Security scanning.
- Support for every language or dynamic import form.

## Product Boundaries

- The AI layer recommends context and prose; it never edits source code.
- Core functionality must work without an API key.
- Source analysis and generated artifacts are local-first.
- The MVP graph is directed and file-level.
- Generated output belongs only under `.vibegraph/`.

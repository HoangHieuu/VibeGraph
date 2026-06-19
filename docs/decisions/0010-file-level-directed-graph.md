# 0010 File-Level Directed Graph

Date: 2026-06-19

## Status

Accepted

## Context

The hackathon timeline cannot support complete semantic code intelligence, but
the product still needs a useful, explainable structure for visualization,
warnings, and context ranking.

## Decision

The MVP graph is a directed file-level import graph for Python, JavaScript, JSX,
TypeScript, and TSX:

```text
File A imports File B
A -> B
```

Function-level call graphs and complete dynamic-import resolution are out of
scope. Unresolved relationships remain explicit graph states instead of
causing scan failure.

## Alternatives Considered

1. Function- or symbol-level semantic graph.
2. Folder-only architecture graph.
3. Undirected file relationship graph.

## Consequences

Positive:

- The model is fast enough for a hackathon MVP.
- Direction supports dependency inspection, warnings, and graph-distance
  ranking.
- Incomplete resolution can be explained honestly.

Tradeoffs:

- Some dynamic or aliased imports remain unresolved.
- Symbol-removal warnings are approximate.

## Follow-Up

- Benchmark common parser patterns before expanding language semantics.

# Analysis and Graph Contract

## Supported Source Files

Included extensions:

```text
.py .js .jsx .ts .tsx
```

Ignored directories include dependency, environment, cache, build, coverage,
framework-output, VCS, and VibeGraph output directories. Lockfiles, source
maps, and minified JavaScript are ignored by default.

## File Records

Each scanned file records:

- Repository-relative path.
- Language.
- Approximate LOC.
- Byte size.
- Last-modified timestamp.

Paths exposed through graph data and APIs are repository-relative unless a
field explicitly documents an absolute project root.

## Parsing

Python support includes:

- `import module`
- `import module as alias`
- `from module import symbol`
- Top-level functions and classes

JavaScript and TypeScript support includes:

- Default, named, and namespace imports
- Simple dynamic imports
- Exported functions, classes, constants, and defaults

Unresolved imports produce structured unresolved or broken edges; they must not
crash a scan.

## Graph Contract

The graph is directed:

```text
File A imports File B
A -> B
```

Node types:

```text
file folder entrypoint test config unknown
```

Edge types:

```text
imports imports_symbol dynamic_import test_targets broken_import
```

Nodes include identity, path, label, language, type, grouping, LOC, degree
counts, entrypoint/orphan state, warning state, and a derived risk score.

Links include source, target, edge type, imported symbols, and health status.

## Graph Artifact

`.vibegraph/graph.json` contains:

- Absolute `projectRoot`.
- Generation timestamp.
- `nodes`.
- `links`.
- Scan statistics.

The frontend and context workflow consume the same graph artifact/API model.

## Watcher and Warnings

Supported source changes use a cross-platform polling observer, with a 100 ms
poll interval and 750 ms debounce. A full graph rebuild after a change is the
MVP behavior.

Warning types:

```text
BROKEN_IMPORT
DELETED_IMPORTED_FILE
MISSING_EXPORTED_SYMBOL
NEW_ORPHAN_FILE
NEW_CIRCULAR_DEPENDENCY
```

Warnings are written to `.vibegraph/warnings.json`, streamed to the dashboard,
and reflected in affected node/edge visual state.

The warning artifact represents current active warnings. Missing-symbol,
deleted-imported-file, newly orphaned-file, and new-cycle warnings compare the
previous and current graph state. Restoring a valid dependency clears its
active warning on the next rebuild.

## Accuracy Boundary

The MVP prioritizes common static import patterns and useful failure reporting.
Complex aliases and dynamic imports may remain unresolved. Uncertainty must be
represented in graph data rather than silently inventing a relationship.

# Delivery and Validation Contract

## Delivery Phases

| Phase | Outcome |
| --- | --- |
| 0 | Workspaces, local dev flow, health connection, output directory |
| 1 | Scanner, import parsing, graph engine, graph JSON |
| 2 | Interactive Obsidian-like dashboard |
| 3 | Context packs and offline/provider behavior |
| 4 | README generation and Mermaid output |
| 5 | Watcher and dependency warnings |
| 6 | npm packaging, landing page, demo, submission polish |

Only the selected phase should be decomposed into active story packets. Later
phases remain backlog candidates until selected.

## Performance Targets

- First graph in under 30 seconds for the demo repository.
- Warning visible in under 2 seconds after save.
- Dashboard usable with at least 100 graph nodes.
- Context pack in under 10 seconds.
- README generation in under 15 seconds.
- Recommended context contains at least 60% fewer files than the full repo.

## Demo Contract

The demo repository uses FastAPI, React, and simple agent tools. The primary
scenario:

1. Launch with one command.
2. Inspect an auth-related graph neighborhood.
3. Rename or remove `validate_session`.
4. Observe a broken-symbol warning.
5. Request context for fixing auth error handling.
6. Receive the auth route, session service, error model, and relevant test.
7. Open the generated context file.
8. Generate a README with a Mermaid diagram.

The complete demo should fit within five minutes.

## Validation Ladder

| Layer | Expected proof |
| --- | --- |
| Unit | Pure scanner, parser, graph, warning, ranking, and formatting rules |
| Integration | FastAPI routes, filesystem artifacts, watcher, provider fallback |
| E2E | Search, node inspection, filters, context pack, README, warning flow |
| Platform | CLI argument/path/process/browser behavior and npm packaging |
| Release | Fresh demo-repo launch and recorded full demo |

## MVP Completion

The MVP is complete only when the one-command launch, supported-language scan,
graph artifact and dashboard, search and inspection, graph modes, context and
README outputs, watcher warnings, offline mode, optional provider mode, demo
repository, landing page, and full demo are all implemented with recorded
proof.

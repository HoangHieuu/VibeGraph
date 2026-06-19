# VibeGraph Product Contracts

These files are the living product contract derived from `SPEC.md`.

| File | Contract |
| --- | --- |
| `overview.md` | Users, problem, goals, non-goals, and success definition |
| `runtime-and-cli.md` | Local runtime, language stack, CLI, output files, and provider behavior |
| `analysis-and-graph.md` | Scanner, parsers, directed graph, watcher, and warnings |
| `dashboard-and-workflows.md` | Dashboard, file inspection, context packs, README generation, and API |
| `delivery-and-validation.md` | Delivery phases, demo contract, performance targets, and MVP completion |

## Source Rule

`SPEC.md` remains the accepted source specification and historical input.
After this decomposition, changes to product behavior must update:

1. The affected file in this directory.
2. The selected story packet.
3. `docs/TEST_MATRIX.md` and durable story proof.
4. A decision record when architecture, scope, API behavior, or validation
   requirements change materially.

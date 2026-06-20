# VibeGraph Story Backlog

Phases 0 through 5 have recorded implementation proof. Later epics remain
unsliced until their work is selected.

## Candidate Epics

| Epic | Description | Status |
| --- | --- | --- |
| E00 | Project foundation and stable generated-output boundary | implemented |
| E01 | Scanner, language parsing, import resolution, graph JSON | implemented |
| E02 | Interactive graph dashboard and file inspection | implemented |
| E03 | Context pack ranking, offline heuristics, provider enhancement | implemented |
| E04 | Deterministic and provider-enhanced README generation | implemented |
| E05 | Realtime watcher and dependency warnings | implemented |
| E06 | npm packaging, landing page, demo repo, submission | in_progress |

## Selected Stories

| Story | Title | Lane | Status |
| --- | --- | --- | --- |
| US-001 | Local development foundation | normal | implemented |
| US-002 | Stable output directory | normal | implemented |
| US-101 | Local scanner and graph | normal | implemented |
| US-201 | Interactive graph dashboard | normal | implemented |
| US-301 | Context pack agent | high-risk | implemented |
| US-401 | README generator | high-risk | implemented |
| US-501 | Realtime watcher and warnings | high-risk | implemented |
| US-601 | Installable npm package and bundled local runtime | high-risk | implemented |
| US-602 | Demo repository | normal | implemented |
| US-603 | Landing page | normal | implemented |
| US-604 | Public npm publication | high-risk | implemented |
| US-605 | Project story audit | normal | implemented |

## Future Slicing Rule

Select the next epic only after the current slice has recorded proof. New story
packets must reference the living product contracts rather than copying
acceptance criteria from `SPEC.md` without reconciliation.

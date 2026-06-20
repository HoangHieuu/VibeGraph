# About VibeGraph

## Inspiration

During hackathons, teams move fast. Files change constantly, teammates work in parallel, and AI coding assistants generate or modify code at high speed. This creates a new problem: the codebase grows faster than the team’s understanding of it.

When a builder wants to fix a bug or add a feature, they often do not know which files are actually relevant. Copying a large part of the repository into an AI coding tool can create noisy prompts, consume unnecessary context, and make dependency assumptions harder to inspect.

We built **VibeGraph** to solve this problem for AI-powered builders.

Our idea was simple:

> What if a codebase could behave like a living knowledge graph, and an AI agent could use that graph to recommend a focused starting set of files for a coding task?

VibeGraph turns a local repository into an interactive, node-colored dependency graph and helps builders understand what changed, what broke, and which files are likely to be useful starting context.

---

## What it does

VibeGraph is a local-first codebase visualization, dependency checking, and context-pruning tool. 

A builder can open a terminal inside a project and run:

```bash
npx @hoanghieudev/vibegraph@latest .
```

VibeGraph then bootstraps an isolated Python backend, compiles the file-level import graph, opens a local dashboard, and displays the project as a live interactive graph.

The main features are:

* **One-command local launch**
  Validates the project path, accepts port/model/browser options, starts the packaged local runtime, and opens the React dashboard by default.
* **Interactive Codebase Graph**
  Visualizes Python, JavaScript, JSX, TypeScript, and TSX files as connected nodes colored by detected groups such as frontend, backend, agent/tooling, test, config, and external dependencies.
* **Static Import/Export Analysis**
  Uses Python's `ast` module and regex-based JavaScript/TypeScript parsing to detect common import, export, and dynamic-import patterns. Complex aliases and highly dynamic imports can remain unresolved instead of being guessed.
* **Real-time Architecture Warnings**
  Watches files for changes and alerts builders to broken imports (`BROKEN_IMPORT`), missing exports (`MISSING_EXPORTED_SYMBOL`), deleted imported files (`DELETED_IMPORTED_FILE`), newly orphaned files (`NEW_ORPHAN_FILE`), and new circular dependencies (`NEW_CIRCULAR_DEPENDENCY`).
* **Graph-Aware Context Recommendation**
  Ranks a focused starting set of files for a task by combining path and symbol matching, graph-distance BFS traversal, file risk, recency, and optional test relevance.
* **Context Pack Generation**
  Writes recommended file paths, selection reasons, copyable `@file` mentions, a suggested prompt, and context-size estimates to `.vibegraph/context.md`. It does not copy source-file contents into the artifact.
* **README Generation**
  Generates a structured project README draft with an overview, architecture summary, modules, run commands, key files, warnings, and a bounded Mermaid diagram.

---

## How we built it

VibeGraph is built as a lightweight monorepo comprising three main boundaries:

### 1. Node.js CLI Orchestrator (`cli/`)
Built with TypeScript and compiled to ES modules, the CLI manages:
- **Environment Isolation**: Requires Python 3.11 or newer, resolves a platform-specific cache path (`Library/Caches` on macOS, `AppData/Local` on Windows, or `.cache`/`XDG_CACHE_HOME` on Linux), and creates a checksum-keyed virtual environment with the standard `venv` and `pip` modules. The environment is reused while the bundled backend manifest remains unchanged.
- **Process Management**: Parses the project path, port, browser, and model options; launches the FastAPI server; waits for its health endpoint; opens the browser by default; and forwards shutdown signals.

### 2. Python Backend Services (`backend/`)
Built with FastAPI and NetworkX, the backend operates the analytical core:
- **Repository Scanning**: Performs a full scan of supported source files. Python files use the native `ast` library; JavaScript and TypeScript files use regex-based extraction for common default, named, namespace, side-effect, and dynamic imports plus common export declarations.
- **Dependency Analytics**: Uses NetworkX to build a directed graph (\(\mathcal{G} = (\mathcal{V}, \mathcal{E})\)), calculate in/out degree and a degree-derived risk score, and detect dependency cycles.
- **File Watching**: Employs a cross-platform polling filesystem watcher (`watchdog.observers.polling.PollingObserver`) with a 100 ms poll interval and a 750 ms debounce. A supported change triggers a full graph rebuild, followed by WebSocket delivery of the updated graph and active warnings.
- **OpenRouter LLM Integration**: Optionally enhances context-pack and README wording using structured graph metadata with a 25-second timeout and deterministic fallback. Source-file contents are not sent to the provider.

### 3. React Dashboard (`frontend/`)
A single-page app built with React, Vite, TypeScript, and Tailwind CSS v4:
- **Graph Layout**: Renders a 2D force-directed canvas using `react-force-graph-2d`, with collision and radial forces from `d3-force-3d`.
- **Interactive Workspace**: Receives graph and warning updates over WebSockets and provides search, filters, file inspection, a warning console, context-pack generation, and README generation.

---

## The Math Behind Context Recommendation

Rather than relying on plain-text vector search, VibeGraph evaluates candidates using structural graph topology and keyword overlap. 

For a task \(T\), VibeGraph calculates a compound score \(S(u)\) for each eligible file node \(u\) using the following deterministic heuristic:

\[
S(u) = S_{\text{text}}(u) + S_{\text{graph}}(u, \mathcal{S}_{\text{seed}}) + S_{\text{metadata}}(u)
\]

### 1. Textual Relevance \(S_{\text{text}}(u)\)
Determines whether a file is explicitly targeted by matching its path, filename, path tokens, and exported-symbol tokens against the task:

\[
S_{\text{text}}(u) = W_{\text{name}}(u,T) + 18 \cdot |T_{\text{tokens}} \cap P_{u,\text{tokens}}| + 24 \cdot |T_{\text{tokens}} \cap E_{u,\text{symbols}}|
\]

where:

\[
W_{\text{name}}(u,T) =
\begin{cases}
120 & \text{if the full path appears in the task} \\
95 & \text{else if the filename appears in the task} \\
0 & \text{otherwise}
\end{cases}
\]

- \(p_u\) is the repository-relative file path, and \(\ell_u\) is its filename.
- \(T_{\text{tokens}}\), \(P_{u,\text{tokens}}\), and \(E_{u,\text{symbols}}\) are normalized token sets for the task, path, and exported symbols.

### 2. Topological Graph Proximity \(S_{\text{graph}}(u, \mathcal{S}_{\text{seed}})\)
Finds the shortest-path distance \(d(u, s)\) from node \(u\) to the seed set \(\mathcal{S}_{\text{seed}}\) using Breadth-First Search (BFS) up to the configured maximum depth. Traversal treats import edges in both directions so that dependencies and importers can both contribute context. Seeds come from explicitly named files when possible, otherwise from the strongest base scores or the most connected nodes.

\[
S_{\text{graph}}(u, \mathcal{S}_{\text{seed}}) = f\left(\min_{s \in \mathcal{S}_{\text{seed}}} d(u, s)\right)
\]

where the distance-based weight decay function \(f(d)\) is defined as:

\[
f(d) = \begin{cases} 
65 & d = 0 \\
56 & d = 1 \\
25 & d = 2 \\
10 & d = 3 \\
4 & d = 4 \\
0 & d > 4 
\end{cases}
\]

### 3. Metadata & State Relevance \(S_{\text{metadata}}(u)\)
Applies adjustment scores based on entrypoint status, the degree-derived risk score, modification recency, and test relevance:

\[
S_{\text{metadata}}(u) = 3 \cdot \mathbb{I}(\text{entrypoint}) + 5 \cdot \text{risk}(u) + \max\left(0,4-\frac{\text{ageDays}(u)}{30}\right) + 12 \cdot \mathbb{I}(\text{included test})
\]

The risk term is normalized from total local graph degree and rounded to three
decimal places:

\[
\text{risk}(u)=
\operatorname{round}\left(
\frac{\log\left(1+\deg_{\text{in}}(u)+\deg_{\text{out}}(u)\right)}
{\log\left(1+D_{\max}\right)},3\right)
\]

where \(D_{\max}\) is the maximum total degree in the current graph.

The top \(k\) eligible files sorted by \(S(u)\) form the recommended starting context. By default, \(k=8\), graph depth is limited to 2, tests are included, and config/docs files are excluded.

---

## Challenges we faced

1. **Cross-Platform Python Bootstrapping**
   We wanted VibeGraph to launch like an npm tool while still running a Python analysis backend. The packaged CLI therefore checks for Python 3.11+, creates a checksum-keyed virtual environment with `venv`, installs the bundled backend with `pip`, and stores the environment in the user's platform cache instead of the analyzed repository. GitHub Actions and package smoke tests verify this flow on Ubuntu and Windows, with additional local proof on macOS.

2. **Debounced Realtime File Watching**
   A branch switch or generated build can produce a burst of filesystem events. We implemented a `ProjectWatcher` that polls every 100 ms, debounces supported changes for \(0.75\) seconds, and ignores directories such as `node_modules`, `.git`, `.venv`, build outputs, caches, and `.vibegraph`. The MVP then performs one full graph rebuild for the batch and broadcasts the complete updated state. In the demo validation, a missing-symbol warning appeared in 0.819 seconds after the file change.

3. **Balancing Visual Noise and Clarity**
   Codebases can have hundreds of files, leading to a "hairball" visualization. To combat visual clutter, we implemented degree-based node sizing, neighborhood hover highlighting (which dims unrelated files and highlights immediate importers and dependencies), path/filename search, and filters for test, config, and orphan files.

---

## What we learned

* **Context Quality > Context Window Size**
  We learned to treat context selection as a retrieval problem instead of assuming that more files are always better. VibeGraph reports the selected files, reasons, estimated tokens, and estimated reduction so builders can inspect the recommendation before giving it to another AI tool. We have not yet run a controlled benchmark proving accuracy or hallucination reduction.
* **Offline-First Resilience**
  Scanning, graph generation, visualization, warnings, deterministic context selection, and README generation work without an LLM key. OpenRouter is an optional wording enhancer rather than a requirement for the core workflow.
* **Unified Visual and Analytical Systems**
  Using the same directed graph for visualization, warnings, file inspection, and context ranking makes each recommendation inspectable: builders can see the selected file's imports, importers, graph neighbors, and scoring reasons instead of receiving an unexplained list.

---

## What's next

* **MCP (Model Context Protocol) Server**
  Expose the local VibeGraph API as an MCP server so MCP-capable coding agents can programmatically inspect import links and query subgraphs during editing.
* **Deeper TSConfig / Path Mapping Resolution**
  Resolve alias imports (e.g., `@components/*`) and custom Python `sys.path` layouts natively across workspace configurations.
* **Multi-Language Expansion**
  Add scanner support for Go, Rust, and C++ to bring graph-aware context pruning to system codebases.

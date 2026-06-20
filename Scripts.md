# VibeGraph Video Demo Script

Target duration: **2 minutes 45 seconds**

## Before Recording

1. Revoke the API key that was exposed on screen or in chat and create a new
   OpenRouter key.
2. Never show the key or the `.env` file in the recording.
3. Restore and validate the demo:

   ```bash
   pnpm demo:restore
   pnpm demo:check
   ```

4. Set the new key in the terminal before recording:

   ```bash
   export OPENROUTER_API_KEY="your-new-openrouter-key"
   ```

5. Prepare two terminal windows:
   - **Terminal 1:** launch VibeGraph.
   - **Terminal 2:** run `pnpm demo:break` and `pnpm demo:restore`.
6. Set browser zoom to a level where the graph, controls, and file inspector
   are visible together.
7. Close notifications, unrelated tabs, and any windows containing secrets.

## Full Demo Script

### 0:00–0:15 — Introduce the problem

**Action**

Show a simple title card or the VibeGraph landing page:

> VibeGraph — Live codebase maps for AI-powered builders

**Narration**

> When a codebase changes quickly, especially during a hackathon, it becomes
> difficult to know which files matter for the next task. Sending an entire
> repository to an AI coding assistant creates noisy context and hides
> dependency risks. VibeGraph turns the repository into a live dependency
> graph and recommends a focused starting set of files.

---

### 0:15–0:32 — Launch with one command

**Action**

Switch to Terminal 1 and run:

```bash
npx @hoanghieudev/vibegraph@latest demo --port 8732 --model deepseek/deepseek-v4-flash
```

Let the browser open automatically. Cut any long installation wait from the
final video.

**Narration**

> I can launch VibeGraph locally with one command. It creates an isolated
> Python environment, starts the packaged FastAPI backend, scans the selected
> project, and opens the React dashboard. DeepSeek is optional and is used
> only to improve generated wording; the core analysis still works offline.

---

### 0:32–0:58 — Explore the dependency graph

**Action**

1. Briefly point to the file and link counts in the left sidebar.
2. Hover over several graph nodes to highlight their direct neighborhood.
3. Search for `auth_routes.py`.
4. Select `backend/app/routes/auth_routes.py`.
5. Point to its imports, importers, exports, and warning status in the file
   inspector.

**Narration**

> Each node is a source file, and each connection represents an import
> relationship. Files are colored by their detected role, such as frontend,
> backend, test, or configuration. I can search for a file, focus its immediate
> neighborhood, and inspect what it imports, what depends on it, and which
> symbols it exports.

---

### 0:58–1:24 — Demonstrate a real-time architecture warning

**Action**

1. Keep the dashboard visible.
2. Switch briefly to Terminal 2 and run:

   ```bash
   pnpm demo:break
   ```

3. Return immediately to the dashboard.
4. Show the warning count changing and the
   `MISSING_EXPORTED_SYMBOL` warning for `validate_session`.
5. Select the affected red node or point to the warning in the file inspector.

**Narration**

> Now I will simulate a common breaking change by removing an exported symbol.
> VibeGraph watches the repository, rebuilds the graph, and reports the issue
> in near real time. Here it detects that `auth_routes.py` still imports
> `validate_session`, but the session service no longer exports it. This makes
> a dependency failure visible before I waste time debugging it elsewhere.

---

### 1:24–2:05 — Generate a graph-aware context pack

**Action**

1. Click **Context pack**.
2. Enter:

   ```text
   Fix login error handling in auth_routes.py
   ```

3. Click **Generate context pack**.
4. Show the result mode and model.
5. Slowly scroll through the recommended files, especially:
   - `backend/app/routes/auth_routes.py`
   - `backend/app/services/session_service.py`
   - `backend/app/models/errors.py`
   - `backend/tests/test_auth_flow.py`
6. Point to the estimated tokens and context reduction.
7. Point to `.vibegraph/context.md` and the **Copy file mentions** and
   **Copy prompt** actions.

**Narration**

> Instead of copying the whole repository into an AI tool, I describe the task
> I want to complete. VibeGraph combines filename and symbol matching with
> graph distance, file risk, recency, and test relevance. It recommends the
> route, its session dependency, the shared error model, and the relevant auth
> test. I can inspect why each file was selected, see the estimated context
> reduction, and copy the file mentions or a ready-to-use prompt. The result is
> also saved locally to `.vibegraph/context.md`, without copying source code
> into that artifact.

---

### 2:05–2:28 — Generate project documentation

**Action**

1. Close the context panel.
2. Click **Generate README**.
3. Optionally enter:

   ```text
   A FastAPI and React authentication demo used to validate VibeGraph.
   ```

4. Click **Generate README draft**.
5. Show the generated modules, key-file count, warning count, Markdown preview,
   and `.vibegraph/README.generated.md` path.

**Narration**

> The same graph can also generate a structured README draft containing the
> project overview, architecture, important modules, run commands, known
> warnings, and a bounded Mermaid diagram. DeepSeek can improve the prose, but
> the files, commands, warnings, and graph relationships remain grounded in
> VibeGraph's local analysis.

---

### 2:28–2:48 — Restore the demo and close

**Action**

1. Switch to Terminal 2 and run:

   ```bash
   pnpm demo:restore
   ```

2. Return to the dashboard and show the warning clearing.
3. End on the graph or landing page with these links on screen:

   ```text
   Try it: npx @hoanghieudev/vibegraph@latest .
   GitHub: github.com/HoangHieuu/VibeGraph
   ```

**Narration**

> When I restore the symbol, the active warning clears automatically. VibeGraph
> gives AI-powered builders a local, inspectable way to understand a codebase,
> catch dependency breakage, and choose better context. You can try it with
> `npx @hoanghieudev/vibegraph@latest .`, and the source code is available on
> GitHub.

## Recording Notes

- Record at 1080p and keep the mouse movement slow and intentional.
- Use cuts to remove package installation and model-response waiting time.
- Keep terminal text large enough to read.
- Do not open `.env`, browser developer tools, or shell history during the
  recording.
- If the provider is slow, record with deterministic mode or cut the waiting
  period. Do not imply that DeepSeek performs the graph scan or file ranking.
- Keep the final video below three minutes by shortening pauses, not by
  speeding up the screen recording.

## Suggested YouTube Metadata

**Title**

> VibeGraph Demo — Live Dependency Graphs and AI Context Pruning

**Description**

> VibeGraph is a local-first developer tool that turns a repository into a
> live dependency graph, detects architecture breakage, and recommends a
> focused context pack for AI coding tasks.
>
> Try it:
> `npx @hoanghieudev/vibegraph@latest .`
>
> GitHub: https://github.com/HoangHieuu/VibeGraph


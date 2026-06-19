Use **MCP servers**, not traditional plugins. Codex supports MCP in both CLI and IDE extension, with config shared through `~/.codex/config.toml`. ([OpenAI Developers][1])

## Recommended MCP stack for VibeGraph

### 1. Filesystem MCP — **must-have**

Use it so Codex can read/write your repo, create `.vibegraph/` files, edit frontend/backend code, inspect generated JSON/Markdown.

```bash id="sg9acz"
codex mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /absolute/path/to/vibegraph
```

The official filesystem server supports read/write files, directory operations, search, metadata, and directory access control. ([GitHub][2])

### 2. Context7 MCP — **must-have**

Use it for up-to-date docs while building with FastAPI, Vite, Tailwind, `react-force-graph-2d`, NetworkX, Watchdog, Tree-sitter.

```bash id="orqzoz"
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

OpenAI’s Codex MCP docs use Context7 as the example developer-documentation MCP server. ([OpenAI Developers][1])

### 3. Playwright MCP — **strongly recommended**

Use it to let Codex open your local dashboard, test graph UI interactions, click nodes, verify search/filter behavior, and inspect the frontend.

```bash id="bd6jmc"
codex mcp add playwright -- npx -y @playwright/mcp@latest
```

Playwright MCP gives agents browser automation through structured accessibility snapshots and works with MCP clients including Codex. ([Playwright][3])

### 4. GitHub MCP — **recommended**

Use it for issues, PRs, repo inspection, README review, release prep, and Devpost-ready project hygiene.

Prefer read-only or limited toolsets at first.

```bash id="td6iqd"
# If using local GitHub MCP server, configure only needed toolsets:
GITHUB_TOOLSETS="repos,issues,pull_requests" 
```

GitHub’s MCP server supports repo browsing, code file access, issues, PRs, Actions, and code analysis; it also supports toolsets so you can limit available capabilities. ([GitHub][4])

### 5. OpenAI Developer Docs MCP — **useful for Codex setup**

Use this if you want Codex to check official OpenAI/Codex docs while configuring agents, MCP, or OpenAI APIs.

```bash id="l3y9os"
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

OpenAI’s docs MCP is read-only and provides search/page access to OpenAI developer documentation. ([OpenAI Developers][5])

### 6. Figma MCP — **optional**

Use only if you design the landing page or dashboard in Figma first. It helps agents extract design context and generate React/Tailwind code from Figma designs. ([Figma Developers][6])

## Custom MCP you should build later

Create your own **VibeGraph MCP server** after MVP. Expose tools like:

```text id="bn652m"
scan_repo
get_graph
get_file_neighbors
get_warnings
generate_context_pack
generate_readme
```

This would let Codex or Cursor ask VibeGraph directly:

```text id="ytvywx"
Use VibeGraph to find the minimal context for fixing auth.py.
```

That is excellent dogfooding and a strong demo angle.

## My recommended setup order

```text id="uyt66p"
1. Filesystem MCP
2. Context7 MCP
3. Playwright MCP
4. GitHub MCP
5. OpenAI Docs MCP
6. Custom VibeGraph MCP
```

Skip database MCPs for now. VibeGraph MVP uses local JSON/Markdown, so database tools add complexity without value. Also restrict Filesystem MCP to only your project folder and avoid broad home-directory access.

[1]: https://developers.openai.com/codex/mcp "Model Context Protocol – Codex | OpenAI Developers"
[2]: https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md "servers/src/filesystem/README.md at main · modelcontextprotocol/servers · GitHub"
[3]: https://playwright.dev/docs/getting-started-mcp "Playwright MCP | Playwright"
[4]: https://github.com/github/github-mcp-server "GitHub - github/github-mcp-server: GitHub's official MCP Server · GitHub"
[5]: https://developers.openai.com/learn/docs-mcp "Docs MCP | OpenAI Developers"
[6]: https://developers.figma.com/docs/figma-mcp-server/?utm_source=chatgpt.com "Introduction | Developer Docs"

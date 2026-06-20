# Design

## Domain Model

- `ReadmeRequest`: optional project description.
- `ReadmeModule`: deterministic group name, files, entry points, and summary.
- `ReadmeDocument`: mode, model, selected modules and files, Mermaid source,
  rendered Markdown, provider status, and artifact path.
- `ReadmeEnhancement`: provider-returned overview, architecture narrative, and
  optional module-description overrides.

Rules:

- Graph analysis always runs before provider enhancement.
- Entry points and high-degree nodes determine key files.
- Mermaid output is bounded and generated only from healthy internal links.
- Commands are read locally from recognized project metadata.
- Provider output cannot add modules, files, commands, or Mermaid edges.
- Source contents and absolute paths are not provider input.

## Application Flow

```text
optional description
  -> load current graph
  -> inspect local project metadata
  -> select entry points, modules, key files, warnings, and commands
  -> build deterministic README sections and Mermaid graph
  -> optionally enhance bounded prose through OpenRouter
  -> validate enhancement or fall back
  -> render and write .vibegraph/README.generated.md
  -> return parsed response
```

## Interface Contract

```text
POST /api/readme
```

Request fields:

- `description` (optional, maximum 2,000 characters)

Response fields:

- `mode`
- `model`
- `projectName`
- `overview`
- `architecture`
- `modules`
- `entrypoints`
- `keyFiles`
- `commands`
- `warnings`
- `mermaid`
- `markdown`
- `providerMessage`
- `artifactPath`

Provider failures do not change the HTTP success contract when deterministic
generation succeeds.

## Data Model

No database changes. The backend remains the sole writer of
`.vibegraph/README.generated.md`.

## UI / Platform Impact

The existing top-bar action opens a README panel with optional description,
generation state, offline/enhanced status, artifact confirmation, summary
counts, preview, and copy action.

## Observability

Provider status is explicit:

- `offline`
- `enhanced`
- `fallback`

API keys, provider request bodies, source contents, and absolute project paths
are not logged or written to generated artifacts.

## Alternatives Considered

1. Send selected source files to OpenRouter. Rejected for privacy.
2. Let the provider generate the Mermaid diagram. Rejected because diagram
   validity and graph fidelity must be deterministic.
3. Overwrite the repository README. Rejected because generated output must be
   isolated and reversible.

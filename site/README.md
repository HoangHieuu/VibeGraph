# VibeGraph Landing Page

The public VibeGraph product page is a standalone React/Vite workspace.

## Development

```bash
pnpm site:dev
```

Open `http://127.0.0.1:4175`.

## Validation

```bash
pnpm --filter @vibegraph/site typecheck
pnpm --filter @vibegraph/site test
pnpm --filter @vibegraph/site build
```

## Vercel

Create a Vercel project from the main repository and set the Root Directory to
`site`. Vercel will use `site/vercel.json` and publish `site/dist`.

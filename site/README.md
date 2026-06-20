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

Production URL:

https://vibegraph-hoanghieudev.vercel.app

The Vercel project uses `site/vercel.json` and publishes `site/dist`.

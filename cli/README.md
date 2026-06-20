# VibeGraph CLI

VibeGraph scans a local Python, JavaScript, or TypeScript project and opens a
live dependency graph with warnings, graph-aware context packs, and README
generation.

This package requires Node.js 22+ and Python 3.11+. Its first launch creates an
isolated Python environment in the user's cache.

```bash
npx @hoanghieudev/vibegraph@latest . --no-open
```

The package exposes the shorter `vibegraph` executable when installed.

Author: [vibedev](https://github.com/HoangHieuu)

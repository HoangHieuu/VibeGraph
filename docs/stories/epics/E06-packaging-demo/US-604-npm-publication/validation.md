# Validation

## Required Commands

```bash
npm whoami
cd cli
npm publish --dry-run --access public
npm publish --access public
npm view @vibedev/vibegraph version
npx @vibedev/vibegraph@latest . --no-open
```

## Current Evidence

- `npm publish --dry-run --access public` passed for
  `@vibedev/vibegraph@0.1.0`.
- The dry-run artifact contains 36 files, is 146.8 kB compressed, and includes
  the compiled CLI, Python backend, production dashboard, README, and license.
- Actual publication is blocked because `npm whoami` returns `ENEEDAUTH`.

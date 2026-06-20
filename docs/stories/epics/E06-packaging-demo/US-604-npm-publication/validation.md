# Validation

## Required Commands

```bash
npm whoami
cd cli
npm publish --dry-run --access public
npm publish --access public
npm view @hoanghieudev/vibegraph version
npx @hoanghieudev/vibegraph@latest . --no-open
```

## Current Evidence

- `npm publish --dry-run --access public` passed for
  `@hoanghieudev/vibegraph@0.1.0`.
- The dry-run artifact contains 36 files, is 146.8 kB compressed, and includes
  the compiled CLI, Python backend, production dashboard, README, and license.
- `npm whoami` returns `hoanghieudev`.
- The first live publish attempt reached the correct scoped registry endpoint
  but npm returned `E403`: publishing requires a current two-factor
  authentication code or a granular token with publish permission and 2FA
  bypass enabled.

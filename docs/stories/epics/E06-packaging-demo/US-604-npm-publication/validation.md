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

## Acceptance Evidence

- `npm publish --dry-run --access public` passed for
  `@hoanghieudev/vibegraph@0.1.0`.
- The dry-run artifact contains 36 files, is 146.8 kB compressed, and includes
  the compiled CLI, Python backend, production dashboard, README, and license.
- `npm whoami` returns `hoanghieudev`.
- Browser-based npm CLI authentication completed the protected publish. The
  npm debug log records a successful registry `PUT 200`.
- `npm access get status @hoanghieudev/vibegraph` returns `public`.
- `npm view @hoanghieudev/vibegraph version dist-tags.latest --json` returns
  version `0.1.0` and the `latest` tag at `0.1.0`.
- A fresh `npx --yes @hoanghieudev/vibegraph@latest <temp-project> --no-open`
  launch resolved from the public registry, started the packaged runtime, and
  returned HTTP 200 responses from `/api/health` and `/api/graph`.

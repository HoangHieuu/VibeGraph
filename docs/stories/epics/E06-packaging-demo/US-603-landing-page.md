# US-603 Landing Page

## Status

implemented

## Lane

normal

## Product Contract

VibeGraph includes a deployable public landing page that explains the product,
shows the local-first graph workflow, links to GitHub, and presents the scoped
npm install command without unverified claims.

## Relevant Product Docs

- `docs/product/overview.md`
- `docs/product/delivery-and-validation.md`
- `docs/product/runtime-and-cli.md`

## Acceptance Criteria

- The page lives under `site/` as a React/Vite application.
- It includes hero, workflow, product capabilities, privacy, demo, install CTA,
  and footer sections.
- The install command is `npx @hoanghieudev/vibegraph@latest .`.
- GitHub links target `https://github.com/HoangHieuu/VibeGraph`.
- Devpost and video links are omitted until real URLs exist.
- Desktop and mobile browser QA pass without console errors.

## Design Notes

- Visual system: dark graphite, white typography, coral focus, violet graph
  edges, open editorial layout.
- UI surfaces: install-command copy action and section navigation.
- Framework: React, Vite, TypeScript.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | Copy interaction utility/component test |
| Integration | Production build |
| E2E | Desktop and mobile section/interaction QA |
| Platform | Static Vite output suitable for Vercel |
| Release | Public deployment after repository handoff |

## Harness Delta

No new process rule expected.

## Evidence

- Site typecheck, Vitest copy-interaction test, and production build passed.
- Desktop QA passed at 1280x720 and native-reference 1536x1024 widths.
- Mobile QA passed at 390x844.
- The install-copy interaction changed from `Copy` to `Copied`.
- Browser console reported zero warnings and errors after the favicon fix.
- Vercel configuration is present under `site/vercel.json`.

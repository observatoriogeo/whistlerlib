# Whistlerlib documentation site

Docusaurus 3.10 site for [Whistlerlib](https://github.com/observatoriogeo/whistlerlib).
The content under `docs/` is a port of the portable Markdown tree at
`<repo>/docs/`; that source tree still ships in the Python sdist and renders
on GitHub on its own. Edits land here for the Docusaurus version, and in
`<repo>/docs/` for the GitHub-rendered version. Keep them in sync.

## Prerequisites

- Node.js >= 20 (Docusaurus 3.10 requires it).

## Install

```bash
npm ci
```

## Local development

```bash
npm start
```

Opens a dev server at http://localhost:3000 with hot reload. Most changes
appear without a server restart.

## Production build

```bash
npm run build
npm run serve
```

`npm run build` runs the full production compile (the same one CI / deploys
use). `onBrokenLinks: 'throw'` is set in `docusaurus.config.ts`, so any
broken cross-link fails the build. `npm run serve` then previews the
generated `build/` directory at http://localhost:3000.

## TypeScript check

```bash
npm run typecheck
```

## Trailing-slash convention (important)

Hardcoded internal links in `docusaurus.config.ts`, the homepage, and the
homepage feature components must follow the trailing-slash rule documented
in [LINK_CONVENTIONS.md](../LINK_CONVENTIONS.md). The short version:
directory-style doc indexes (`/docs/tutorials/`, `/docs/api/`) keep the
trailing slash; single-page docs (`/docs/quickstart`, `/docs/changelog`)
do not. Getting this wrong produces hard-to-debug 404s on client-side
navigation.

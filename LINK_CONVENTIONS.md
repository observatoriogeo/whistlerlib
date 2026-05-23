# Docusaurus link conventions

Long-form write-up of a subtle URL-resolution gotcha in the Whistlerlib
Docusaurus site under `website/`. Read this if you're editing
`website/docusaurus.config.ts`, the homepage / footer Link components, or
hardcoded `to:` props anywhere in the site. The rule is summarized below;
this file explains the why and the failed alternatives so the next person
(or LLM) doesn't repeat them. The conventions here were validated in the
adjacent Weaverlet docs repo, this file is its Whistlerlib counterpart.

## The rule

For any hardcoded `Link to="..."` or navbar/footer/homepage `to:` prop:

- If the target is a **directory-style docs index** (a doc backed by an
  `index.mdx` file, e.g. `tutorials/index.mdx`, `api/index.mdx`),
  **include the trailing slash**: `to: '/docs/tutorials/'`.
- If the target is a **single-page doc** (no `index.mdx` in a same-named
  subdirectory, e.g. `quickstart.md`, `changelog.mdx`,
  `installation/pip.md`), **omit the trailing slash**:
  `to: '/docs/quickstart'`.

Concrete checklist for this repo's current docs:

| Path | Slash? | Why |
|---|---|---|
| `/docs/tutorials/` | yes | `tutorials/index.mdx` |
| `/docs/api/` | yes | `api/index.mdx` |
| `/docs/installation/pip` | no | single-page child |
| `/docs/installation/docker` | no | single-page child |
| `/docs/concepts/architecture` | no | single-page child |
| `/docs/concepts/context-and-datasets` | no | single-page child |
| `/docs/concepts/algorithm-families` | no | single-page child |
| `/docs/quickstart` | no | single-page top-level |
| `/docs/changelog` | no | single-page top-level |
| `/docs/citation` | no | single-page top-level |
| `/docs/migration/from-0.1.0` | no | single-page child |
| `/docs/tutorials/01-quickstart-hashtag-histogram` | no | single-page child |

The "Core concepts" sidebar group is a category without an `index.mdx`
(just a list of children), so it has no directory-style permalink and its
`link:` in `sidebars.ts` is omitted (it expands to a list of children
when clicked).

## The bug this rule prevents

**Repro pattern** (the one that bit the Weaverlet docs in production):

1. Visit the homepage.
2. Click "Tutorials" in the top navbar (or any nav target with no slash).
3. On the Tutorials index, click a child tutorial link.
4. Land on a 404 page. The `/tutorials/` segment got dropped between
   click and navigation.

**Mechanism**:

1. The navbar item is `{to: '/docs/tutorials', label: 'Tutorials'}`, no
   trailing slash. Clicking it calls `history.push('/docs/tutorials')`
   directly. The server's 301-to-trailing-slash redirect is *not* hit
   because navigation is purely client-side.
2. The browser address bar reads `/docs/tutorials` (no slash). React
   Router's notion of "current location" is also `/docs/tutorials`.
3. The user clicks a child link, source MDX
   `[01](./01-quickstart-hashtag-histogram)`. Relative-link resolution
   against `/docs/tutorials` (no slash) drops the `tutorials` segment
   because URL semantics treat trailing-slash-less paths as files, not
   directories. `./01-quickstart-hashtag-histogram` resolves to
   `/docs/01-quickstart-hashtag-histogram`.
4. React Router pushes that URL. No route exists, SPA renders 404.

**Confirmation**: typing `/docs/tutorials/` (with slash) into the address
bar and then clicking the same child link works correctly. The bug only
hits the client-side navigation from a no-slash entry point.

## The fix that works

Narrow patch: add trailing slashes only to the hardcoded `to:` props that
target directory-style docs indexes. In this repo that means
`/docs/tutorials/` and `/docs/api/` in:

- `website/docusaurus.config.ts` (navbar + footer)
- `website/src/pages/index.tsx` (hero + final callout)
- `website/src/components/HomepageFeatures/index.tsx` (if a card links to
  a directory index)

No MDX edits are needed. Relative MDX links resolve at *build* time
against the source file path, not the URL, so they remain correct
regardless of trailing-slash conventions on the rendered side.

## The fix that does NOT work

`trailingSlash: true` globally in `docusaurus.config.ts` looks like the
clean fix but it flips the canonical URL of every doc. Under
`trailingSlash: true`, source URLs become `/docs/foo/`, so a relative
link `./bar` resolves to `/docs/foo/bar` (child) instead of `/docs/bar`
(sibling). Dozens of relative links across `concepts/` and `tutorials/`
break that way, and `onBrokenLinks: 'throw'` aborts the build. Stay with
the narrow per-nav-prop fix.

## Detection: when to apply the rule

Anywhere a `to:` or `Link to=` prop is hardcoded with a path under
`/docs/`. The MDX-resolved Links built from `[text](./path)` syntax are
handled correctly by Docusaurus at build time and don't need manual
trailing slashes. Only the *hardcoded* `to:` strings need attention.

Quick audit command (run from repo root):

```bash
grep -rnE 'to[:=][[:space:]]*["\x27]/docs/[^"\x27]*["\x27]' \
  website/src website/docusaurus.config.ts
```

For each match, check whether the target doc has an `index.mdx` in a
same-named subdirectory:

```bash
ls website/docs/<path>/index.mdx 2>/dev/null
```

If it does, trailing slash required. If not, no trailing slash.

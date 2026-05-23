import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Whistlerlib',
  // Tagline candidates (user will choose):
  //   "Distributed NLP and social-network analytics on Dask."  [current]
  //   "Hashtags, mentions, sentiment, and co-occurrence networks at cluster scale."
  //   "Twitter-scale analytics. Dask under the hood."
  tagline: 'Distributed NLP and social-network analytics on Dask.',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // GitHub Pages deploys this site to whistlerlib.observatoriogeo.mx
  // (custom domain pinned by website/static/CNAME). Workflow:
  // .github/workflows/docs-deploy.yml.
  url: 'https://whistlerlib.observatoriogeo.mx',
  baseUrl: '/',

  organizationName: 'observatoriogeo',
  projectName: 'whistlerlib',

  onBrokenLinks: 'throw',
  onBrokenAnchors: 'throw',

  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
    [
      // Local search. Configured identically to Weaverlet's docs site.
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en'],
        docsRouteBasePath: '/docs',
        indexBlog: false,
        highlightSearchTermsOnTargetPage: true,
      },
    ],
  ],

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // JSON-LD structured data: helps Google Scholar / Semantic Scholar /
  // OpenAlex match this site to the underlying paper (MTAP 2024). The
  // outer record is the SoftwareApplication; the inner `citation` is the
  // ScholarlyArticle. Update softwareVersion on each release.
  headTags: [
    {
      tagName: 'script',
      attributes: {type: 'application/ld+json'},
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'Whistlerlib',
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Linux, macOS, Windows',
        description:
          'Distributed NLP and social-network analytics for X / Twitter datasets, built on Dask.',
        url: 'https://whistlerlib.observatoriogeo.mx',
        softwareVersion: '0.2.0',
        license: 'https://www.gnu.org/licenses/gpl-3.0.html',
        codeRepository: 'https://github.com/observatoriogeo/whistlerlib',
        author: [
          {
            '@type': 'Person',
            name: 'Alberto Garcia-Robledo',
            affiliation: {'@type': 'Organization', name: 'CentroGeo'},
          },
          {
            '@type': 'Person',
            name: 'Angelina Espejel-Trujillo',
            affiliation: {'@type': 'Organization', name: 'CentroGeo'},
          },
        ],
        citation: {
          '@type': 'ScholarlyArticle',
          name: 'Whistlerlib: a distributed computing library for exploratory data analysis on large social network datasets',
          author: [
            {'@type': 'Person', name: 'Alberto Garcia-Robledo'},
            {'@type': 'Person', name: 'Angelina Espejel-Trujillo'},
          ],
          isPartOf: {
            '@type': 'PublicationVolume',
            volumeNumber: '83',
            isPartOf: {
              '@type': 'Periodical',
              name: 'Multimedia Tools and Applications',
              publisher: {'@type': 'Organization', name: 'Springer'},
            },
          },
          pageStart: '87071',
          pageEnd: '87104',
          datePublished: '2024',
          identifier: 'doi:10.1007/s11042-024-19827-z',
          sameAs: 'https://doi.org/10.1007/s11042-024-19827-z',
          url: 'https://doi.org/10.1007/s11042-024-19827-z',
        },
      }),
    },
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/observatoriogeo/whistlerlib/tree/main/website/',
          // Single labelled version. `current` is Docusaurus' magic key
          // for the live docs/ tree (no snapshot needed). When 0.3.0 is
          // cut, snapshot 0.2.0 via `npm run docusaurus docs:version 0.2.0`
          // and add it to the versions map.
          lastVersion: 'current',
          versions: {
            current: {label: 'v0.2.0'},
          },
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Site-wide meta tags: surface the paper to search engines and social
    // link-preview cards. Per-page tags (Open Graph descriptions on each
    // individual doc) come from each doc's frontmatter and override these.
    metadata: [
      {
        name: 'description',
        content:
          'Whistlerlib: distributed NLP and social-network analytics for X / Twitter datasets, built on Dask. Companion site to the MTAP 2024 paper by Garcia-Robledo and Espejel-Trujillo.',
      },
      {
        name: 'keywords',
        content:
          'Whistlerlib, distributed NLP, social network analytics, Dask, advertools, syuzhet, hashtag co-occurrence networks, Twitter analytics, Garcia-Robledo, Espejel-Trujillo, MTAP 2024, CentroGeo',
      },
      {property: 'og:title', content: 'Whistlerlib: Distributed NLP and social-network analytics on Dask'},
      {
        property: 'og:description',
        content:
          'Companion docs site for Whistlerlib, the MTAP 2024 paper by Garcia-Robledo and Espejel-Trujillo. Hashtags, mentions, n-grams, sentiment ranges, and co-occurrence networks at cluster scale.',
      },
      {property: 'og:type', content: 'article'},
      {property: 'og:url', content: 'https://whistlerlib.observatoriogeo.mx/'},
      {name: 'twitter:card', content: 'summary'},
    ],
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Whistlerlib',
      logo: {
        alt: 'Whistlerlib',
        src: 'img/whistlerlib-logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          // Trailing slash is load-bearing: without it, React Router pushes
          // /docs/tutorials (no slash) on click, and any relative MDX link
          // on that page resolves against the no-slash form and drops the
          // /tutorials/ segment. Same fix applies to /docs/api/ below.
          to: '/docs/tutorials/',
          label: 'Tutorials',
          position: 'left',
        },
        {
          to: '/docs/api/',
          label: 'Reference',
          position: 'left',
        },
        {
          to: '/about',
          label: 'About',
          position: 'left',
        },
        {type: 'docsVersionDropdown', position: 'right'},
        {
          href: 'https://doi.org/10.1007/s11042-024-19827-z',
          label: 'Paper',
          position: 'right',
        },
        {
          href: 'https://pypi.org/project/whistlerlib/',
          label: 'PyPI',
          position: 'right',
        },
        {
          href: 'https://hub.docker.com/r/albertogarob/whistlerlib',
          label: 'Docker Hub',
          position: 'right',
        },
        {
          href: 'https://github.com/observatoriogeo/whistlerlib',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            // Trailing slashes on directory-style targets only (tutorials/, api/);
            // single-page docs (installation/pip, quickstart, changelog) are not
            // directory indexes so they don't need it.
            {label: 'Getting started', to: '/docs/installation/pip'},
            {label: 'Quickstart', to: '/docs/quickstart'},
            {label: 'Tutorials', to: '/docs/tutorials/'},
            {label: 'Reference', to: '/docs/api/'},
            {label: 'Changelog', to: '/docs/changelog'},
          ],
        },
        {
          title: 'Project',
          items: [
            {label: 'GitHub', href: 'https://github.com/observatoriogeo/whistlerlib'},
            {label: 'PyPI', href: 'https://pypi.org/project/whistlerlib/'},
            {label: 'Issues', href: 'https://github.com/observatoriogeo/whistlerlib/issues'},
          ],
        },
        {
          title: 'Authors',
          items: [
            {label: 'CentroGeo', href: 'https://www.centrogeo.org.mx/'},
            {label: 'Observatorio Metropolitano CentroGeo', href: 'https://observatoriogeo.mx'},
            {label: 'SECIHTI', href: 'https://secihti.mx'},
          ],
        },
      ],
      copyright: `Copyright © 2026 Centro de Investigación en Ciencias de Información Geoespacial. GPL-3.0-or-later.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'r', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

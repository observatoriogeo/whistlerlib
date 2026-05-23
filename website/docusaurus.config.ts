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

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/observatoriogeo/whistlerlib/tree/main/website/',
          // TODO (deployment): enable versioning when 0.3.x is cut, see Weaverlet's config for the pattern.
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
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

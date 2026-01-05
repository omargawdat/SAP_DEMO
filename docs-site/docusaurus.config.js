// @ts-check
import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'PII Shield',
  tagline: 'Intelligent PII Detection & De-identification for German Data Protection',
  favicon: 'img/favicon.ico',

  url: 'https://pii-shield.github.io',
  baseUrl: '/',

  organizationName: 'omargawdat',
  projectName: 'pii-shield',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },

  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/pii-shield-social.png',
      navbar: {
        title: 'PII Shield',
        logo: {
          alt: 'PII Shield Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            href: 'https://sap-pii-shield.streamlit.app',
            label: 'Live Demo',
            position: 'left',
          },
          {
            href: 'https://github.com/omargawdat/SAP_DEMO',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Full Documentation',
                to: '/docs',
              },
            ],
          },
          {
            title: 'Demo',
            items: [
              {
                label: 'Live Demo (Streamlit)',
                href: 'https://sap-pii-shield.streamlit.app',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/omargawdat/SAP_DEMO',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} PII Shield - Built for SAP EDT Data Protection Demo`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json'],
      },
      mermaid: {
        theme: { light: 'neutral', dark: 'dark' },
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

export default config;

import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting started',
      collapsed: false,
      items: ['installation/pip', 'installation/docker'],
    },
    'quickstart',
    {
      type: 'category',
      label: 'Core concepts',
      items: [
        'concepts/architecture',
        'concepts/context-and-datasets',
        'concepts/algorithm-families',
      ],
    },
    {
      type: 'category',
      label: 'Tutorials',
      link: {type: 'doc', id: 'tutorials/index'},
      items: [
        'tutorials/01-quickstart-hashtag-histogram',
        'tutorials/02-mention-histogram',
        'tutorials/03-ngram-histogram-bilingual',
        'tutorials/04-sentiment-spanish',
        'tutorials/05-hashtag-coonet',
        'tutorials/06-mention-coonet',
        'tutorials/07-r-bridge-mfhashtags',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      // Only one page for now (api/index). When per-symbol pages land,
      // list them under items: e.g. 'api/context', 'api/tweet-dataset', ...
      link: {type: 'doc', id: 'api/index'},
      items: [],
    },
    'migration/from-0.1.0',
    'changelog',
    'citation',
  ],
};

export default sidebars;

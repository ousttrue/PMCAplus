import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // But you can create a sidebar manually
  tutorialSidebar: [
    'index',
    'history',
    {
      type: 'category',
      label: 'data',
      link: { type: 'doc', id: 'data/index', },
      items: [
        'data/list_txt',
        'data/parts',
        'data/materials',
        'data/transforms',
        'data/cnl',
      ],
    },
    {
      type: 'category',
      label: 'assemble',
      link: { type: 'doc', id: 'assemble/index', },
      items: [
        'assemble/add',
        'assemble/merge',
      ]
    },
  ],
};

export default sidebars;

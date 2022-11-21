// site URLs
export const HOME_URL = '/';
export const BLOG_URL = '/blog';
export const RESEARCH_URL = '/research';
export const TEAM_URL = '/team';
export const EVENTS_URL = '/events';
export const BOUNTIES_URL = '/bounties';

// nav
export const NAV_LINKS = [
  { href: HOME_URL, text: 'home' },
  { href: BLOG_URL, text: 'blog' },
  { href: RESEARCH_URL, text: 'research' },
  { href: BOUNTIES_URL, text: 'bounties' },
  { href: TEAM_URL, text: 'team' },
  { href: EVENTS_URL, text: 'events' }
];

// metadata
export const HEAD_TITLE_LONG = 'Ethereum Foundation Cryptography Research';
export const HEAD_TITLE_SHORT = 'EF Cryptography Research';

// posts
export const POSTS_DIR = 'src/posts';

// bounties data sources
export const BOUNTIES_DATA_SOURCE = 'src/bounties-data-source';
export const LEGENDRE_PRF_DATA_SOURCE = `${BOUNTIES_DATA_SOURCE}/legendre-prf`;
export const ZK_HASH_DATA_SOURCE = `${BOUNTIES_DATA_SOURCE}/zk-hash.md`;
export const RSA_DATA_SOURCE = `${BOUNTIES_DATA_SOURCE}/rsa`;
export const MIMC_HASH_DATA_SOURCE = `${BOUNTIES_DATA_SOURCE}/mimc-hash-challenge.md`;

// bounties URLs
export const MIMC_HASH_BOUNTIES_URL = '/bounties/mimc-hash-challenge';
export const LEGENDRE_PRF_URL = '/bounties/legendre-prf';
export const LEGENDRE_PRF_BOUNTIES_URL = '/bounties/legendre-prf/algorithmic-bounties';
export const LEGENDRE_PRF_CONCRETE_INSTANCES_BOUNTIES_URL =
  '/bounties/legendre-prf/concrete-instance-bounties';
export const ZK_HASH_BOUNTIES_URL = '/bounties/zk-hash';
export const RSA_URL = '/bounties/rsa';
export const RSA_ASSUMPTIONS_URL = '/bounties/rsa/assumptions';

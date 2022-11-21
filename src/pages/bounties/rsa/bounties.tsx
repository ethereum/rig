import type { GetStaticProps, NextPage } from 'next';
import fs from 'fs';
import matter from 'gray-matter';

import Bounty from '../../../components/UI/Bounty';

import { RSA_DATA_SOURCE } from '../../../constants';
import { MarkdownBounty } from '../../../types';

// generate the static props for the page
export const getStaticProps: GetStaticProps = async () => {
  const fileName = fs.readFileSync(`${RSA_DATA_SOURCE}/bounties.md`, 'utf-8');
  const { data: frontmatter, content } = matter(fileName);

  return {
    props: {
      content,
      frontmatter
    }
  };
};

const RSABounties: NextPage<MarkdownBounty> = ({ frontmatter, content }) => {
  const { title, description } = frontmatter;

  return <Bounty title={title} description={description} content={content} />;
};

export default RSABounties;

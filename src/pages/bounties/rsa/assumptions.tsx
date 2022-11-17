import type { GetStaticProps, NextPage } from 'next';
import fs from 'fs';
import matter from 'gray-matter';

import Bounty from '../../../components/UI/Bounty';

import { MarkdownBounty } from '../../../types';
import { RSA_DATA_SOURCE } from '../../../constants';

// generate the static props for the page
export const getStaticProps: GetStaticProps = async () => {
  const fileName = fs.readFileSync(`${RSA_DATA_SOURCE}/assumptions.md`, 'utf-8');
  const { data: frontmatter, content } = matter(fileName);

  return {
    props: {
      content,
      frontmatter
    }
  };
};

const RSAAssumptions: NextPage<MarkdownBounty> = ({ frontmatter, content }) => {
  const { title, description } = frontmatter;

  return <Bounty title={title} description={description} content={content} />;
};

export default RSAAssumptions;

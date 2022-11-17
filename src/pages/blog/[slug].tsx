/* eslint-disable react/no-children-prop */
import fs from 'fs';
import type { GetStaticPaths, GetStaticProps, NextPage } from 'next';
import matter from 'gray-matter';
import ReactMarkdown from 'react-markdown';
import gfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { Heading } from '@chakra-ui/react';
import ChakraUIRenderer from 'chakra-ui-markdown-renderer';

import { PageMetadata } from '../../components/UI';
import { PostTheme } from '../../components/styles/';

import { getParsedDate } from '../../utils';

import { POSTS_DIR } from '../../constants';

// generating the paths for each post
export const getStaticPaths: GetStaticPaths = () => {
  // check if any .md post file exists, don't generate the paths otherwise
  if (!fs.existsSync(POSTS_DIR)) {
    return {
      paths: [],
      fallback: false
    };
  }

  // get list of all files from our posts directory
  const files = fs.readdirSync(POSTS_DIR);
  // generate a path for each one
  const paths = files.map(fileName => ({
    params: {
      slug: fileName.replace('.md', '')
    }
  }));
  // return list of paths
  return {
    paths,
    fallback: false
  };
};

// generate the static props for the page
export const getStaticProps: GetStaticProps = async context => {
  const slug = context.params?.slug as string;
  const fileName = fs.readFileSync(`${POSTS_DIR}/${slug}.md`, 'utf-8');
  const { data: frontmatter, content } = matter(fileName);

  return {
    props: {
      frontmatter,
      content
    }
  };
};

interface Props {
  frontmatter: {
    [key: string]: any;
  };
  content: string;
}

const Post: NextPage<Props> = ({ frontmatter, content }) => {
  const { title, author, date, description } = frontmatter;
  const parsedDate = getParsedDate(date);

  return (
    <>
      <PageMetadata title={title} description={description} />

      <main>
        <Heading as='h1' mb={1}>
          {title}
        </Heading>

        <Heading as='h2' fontSize='sm' fontWeight={400} mb={16} color='gray.500'>
          {author} | {parsedDate}
        </Heading>

        <ReactMarkdown
          components={ChakraUIRenderer(PostTheme)}
          children={content}
          remarkPlugins={[gfm, remarkMath]}
          rehypePlugins={[rehypeKatex, rehypeRaw]}
        />
      </main>
    </>
  );
};

export default Post;

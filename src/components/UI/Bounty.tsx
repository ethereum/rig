/* eslint-disable react/no-children-prop */
import { Heading } from '@chakra-ui/react';
import { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import gfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import ChakraUIRenderer from 'chakra-ui-markdown-renderer';

import { PageMetadata } from '.';
import { PostTheme } from '../styles';

interface Props {
  title: string;
  description: string;
  content: string;
}

const Bounty: FC<Props> = ({ title, description, content }) => {
  return (
    <>
      <PageMetadata title={title} description={description} />

      <main>
        <Heading as='h1' mb={20}>
          {title}
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

export default Bounty;

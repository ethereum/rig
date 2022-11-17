import fs from 'fs';
import matter from 'gray-matter';
import { Heading, Stack } from '@chakra-ui/react';
import type { GetStaticProps, NextPage } from 'next';
// import TweetEmbed from 'react-tweet-embed';

import { ExternalPost, InternalPost, PageMetadata } from '../../components/UI';

import { getParsedDate, sortByDate } from '../../utils';

import { MarkdownPost } from '../../types';
import { POSTS_DIR } from '../../constants';

export const getStaticProps: GetStaticProps = async context => {
  // get list of files from the posts folder
  const files = fs.existsSync(POSTS_DIR) ? fs.readdirSync(POSTS_DIR) : [];

  // get frontmatter & slug from each post
  const posts = files.map(fileName => {
    const slug = fileName.replace('.md', '');
    const readFile = fs.readFileSync(`${POSTS_DIR}/${fileName}`, 'utf-8');
    const { data: frontmatter } = matter(readFile);

    return {
      slug,
      frontmatter
    };
  });

  // return the pages static props
  return {
    props: {
      posts
    }
  };
};

interface Props {
  posts: MarkdownPost[];
}

// add here the list of external blog posts, with title, date and link
const externalLinks = [
  {
    title: 'A Universal Verification Equation for Data Availability Sampling',
    date: '2022-08-04',
    link: 'https://ethresear.ch/t/a-universal-verification-equation-for-data-availability-sampling/13240'
  },
  {
    title: 'Whisk: A practical shuffle-based SSLE protocol for Ethereum',
    date: '2022-01-13',
    link: 'https://ethresear.ch/t/whisk-a-practical-shuffle-based-ssle-protocol-for-ethereum/11763'
  },
  {
    title: 'Introducing Bandersnatch: a fast elliptic curve built over the BLS12-381 scalar field',
    date: '2021-06-29',
    link: 'https://ethresear.ch/t/introducing-bandersnatch-a-fast-elliptic-curve-built-over-the-bls12-381-scalar-field/9957'
  },
  {
    title: 'Inner Product Arguments',
    date: '2021-06-27',
    link: 'https://dankradfeist.de/ethereum/2021/07/27/inner-product-arguments.html'
  },
  {
    title: 'PCS multiproofs using random evaluation',
    date: '2021-06-18',
    link: 'https://dankradfeist.de/ethereum/2021/06/18/pcs-multiproofs.html'
  },
  {
    title: 'VDF Proving with SnarkPack',
    date: '2020-07-16',
    link: 'https://ethresear.ch/t/vdf-proving-with-snarkpack/10096/1'
  },
  {
    title: 'KZG polynomial commitments',
    date: '2020-06-16',
    link: 'https://dankradfeist.de/ethereum/2020/06/16/kate-polynomial-commitments.html'
  }
];

const Blog: NextPage<Props> = ({ posts }) => {
  const internalPosts = posts.map(post => {
    //extract slug and frontmatter
    const { slug, frontmatter } = post;
    //extract frontmatter properties
    const { title, date } = frontmatter;
    const parsedDate = getParsedDate(date);

    //JSX for individual blog listing
    return <InternalPost key={slug} date={date} slug={slug} title={title} />;
  });

  const externalPosts = externalLinks.map(({ date, link, title }) => (
    <ExternalPost key={link} date={date} link={link} title={`${title} ↗`} />
  ));

  return (
    <>
      <PageMetadata
        title='Blog'
        description='View latest posts from the Ethereum Foundation Cryptography Research team.'
      />

      <main>
        <Heading as='h1' mb={10}>
          Blog
        </Heading>

        <Stack spacing={2}>{internalPosts.concat(externalPosts).sort(sortByDate)}</Stack>

        {/* <HStack spacing={8} alignItems='flex-start' wrap='wrap'>
          <TweetEmbed tweetId='1506958509195374598' />

          <TweetEmbed tweetId='1508538717660663809' />

          <TweetEmbed tweetId='1508474058748403716' />
        </HStack> */}
      </main>
    </>
  );
};

export default Blog;

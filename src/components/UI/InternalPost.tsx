import { Heading, Link } from '@chakra-ui/react';
import { FC } from 'react';
import NextLink from 'next/link';

import { getParsedDate } from '../../utils';

interface Props {
  date: string;
  slug: string;
  title: string;
}

export const InternalPost: FC<Props> = ({ date, slug, title }) => {
  const parsedDate = getParsedDate(date);

  return (
    <article key={title}>
      <Heading as='h3' fontSize='sm' fontWeight={400} mb={1}>
        {parsedDate}
      </Heading>

      <NextLink href={`blog/${slug}`} passHref>
        <Link
          href={`blog/${slug}`}
          color='brand.lightblue'
          _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
        >
          <Heading as='h1' mb={4} fontSize='xl' fontWeight={500}>
            {title}
          </Heading>
        </Link>
      </NextLink>
    </article>
  );
};

import { Heading, Link } from '@chakra-ui/react';
import { FC } from 'react';
import NextLink from 'next/link';

import { getParsedDate } from '../../utils';

interface Props {
  date: string;
  link: string;
  title: string;
}

export const ExternalPost: FC<Props> = ({ date, link, title }) => {
  const parsedDate = getParsedDate(date);

  return (
    <article>
      <Heading as='h3' fontSize='sm' fontWeight={400} mb={1}>
        {parsedDate}
      </Heading>

      <NextLink href={link} passHref>
        <Link
          href={link}
          color='brand.lightblue'
          _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
          isExternal
        >
          <Heading as='h1' mb={4} fontSize='xl' fontWeight={500}>
            {title}
          </Heading>
        </Link>
      </NextLink>
    </article>
  );
};

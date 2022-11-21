import { Link, Stack, Text } from '@chakra-ui/react';
import { FC } from 'react';

import { Abstract } from './Abstract';

interface Props {
  title: string;
  authors: string;
  conference: string;
  link: string;
}

export const Publication: FC<Props> = ({ title, authors, conference, link, children }) => {
  return (
    <Stack>
      <Text mb={-1} fontWeight='bold'>
        {title}.
      </Text>
      <Text fontSize='sm'>
        <em>{authors}.</em>
      </Text>
      <Text fontSize='sm'>
        {conference}{' '}
        <Link
          href={link}
          color='brand.lightblue'
          _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
          isExternal
        >
          PDF.
        </Link>
      </Text>

      <Abstract>{children}</Abstract>
    </Stack>
  );
};

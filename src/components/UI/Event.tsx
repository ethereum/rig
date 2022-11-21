import { Heading, Link, Stack, Text } from '@chakra-ui/react';
import { FC } from 'react';

interface Props {
  conference: string;
  workshop: string;
}

export const Event: FC<Props> = ({ conference, workshop, children }) => {
  return (
    <Stack>
      <Heading as='h2' fontSize='3xl' fontWeight={600} mb={2}>
        {conference}
      </Heading>

      <Text mb={10}>
        <Link
          href='https://sites.google.com/view/cryptographic-frontier-2022/'
          color='brand.lightblue'
          _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
          isExternal
        >
          <strong>{workshop}:</strong>
        </Link>{' '}
        {/* workshop description */}
        {children}
      </Text>
    </Stack>
  );
};

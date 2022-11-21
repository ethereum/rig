import { Box, Container, Stack } from '@chakra-ui/react';
import { FC } from 'react';

import { Footer, Header } from '../UI';

export const Layout: FC = ({ children }) => {
  return (
    <>
      {/* <Container maxW={{ lg: 'container.lg' }} px={0}> */}
      <Header />
      {/* </Container> */}

      <Container
        maxW={{ base: 'container.md', lg: 'container.lg', xl2: 'container.xl' }}
        px={{ base: 6, md: 16, lg: 8, xl: 10 }}
        py={{ base: 16, lg: 12 }}
      >
        <Stack mt={{ base: 4, xl: 12 }} mb={32}>
          {children}
        </Stack>

        <Footer />
      </Container>
    </>
  );
};

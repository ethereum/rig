import { Heading, Text } from '@chakra-ui/react';
import type { NextPage } from 'next';

import { PageMetadata } from '../components/UI';

const Home: NextPage = () => {
  return (
    <>
      <PageMetadata
        title='Home'
        description='Cryptography research group at the Ethereum Foundation.'
      />

      <main>
        <Heading as='h1' mb={10}>
          Cryptography Research at the Ethereum Foundation
        </Heading>

        <Text>
          The Ethereum Foundation leads research into cryptographic protocols that are useful within
          the greater Ethereum community and more generally. Cryptography is a key tool that enables
          greater functionality, security, efficiency, and auditability in decentralized settings.
          We are currently conducting research into verifiable delay functions, multiparty
          computation, vector commitments, and zero-knowledge proofs etc. We have a culture of open
          source and no patents are put on any work that we produce.
        </Text>
      </main>
    </>
  );
};

export default Home;

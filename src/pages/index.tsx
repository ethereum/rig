import { Heading, Text } from '@chakra-ui/react';
import type { NextPage } from 'next';

import { PageMetadata } from '../components/UI';

const Home: NextPage = () => {
  return (
    <>
      <PageMetadata
        title='Home'
        description='Robust Incentives Group at the Ethereum Foundation.'
      />

      <main>
        <Heading as='h1' mb={10}>
          Robust Incentives Group at the Ethereum Foundation
        </Heading>

        <Text>
          The Robust Incentives Group is a research team of the Ethereum Foundation. We specialise
          in incentive analysis for protocols, using methods from game theory, mechanism design,
          empirical analysis and simulations. Since our foundation, we actively participated in
          research on EIP-1559 and Proof-of-Stake Ethereum. Find our releases, posts, and papers on
          this website!
        </Text>
      </main>
    </>
  );
};

export default Home;

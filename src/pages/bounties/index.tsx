import { Heading, Stack } from '@chakra-ui/react';
import type { NextPage } from 'next';

import { BountyCard, PageMetadata } from '../../components/UI/';

import {
  LEGENDRE_PRF_URL,
  MIMC_HASH_BOUNTIES_URL,
  RSA_URL,
  ZK_HASH_BOUNTIES_URL
} from '../../constants';

const Bounties: NextPage = () => {
  return (
    <>
      <PageMetadata
        title='Bounties'
        description='Find Ethereum bounties related to cryptography. '
      />

      <main>
        <Heading as='h1' mb={10}>
          Bounties
        </Heading>

        <Stack spacing={4}>
          <BountyCard
            url={RSA_URL}
            title='RSA Bounties'
            postedBy='Ethereum Foundation'
            totalBounty='$28,000 USD and 28 ETH'
          >
            For the Verifiable Delay Function (VDF) project, the RSA Low Order and Adaptive Root
            assumptions have come into spotlight as they are required for the two VDF proof
            construction. Several bounties are available for proving or disproving the assumptions.
          </BountyCard>

          <BountyCard
            url={LEGENDRE_PRF_URL}
            title='Legendre PRF Bounties'
            postedBy='Ethereum Foundation'
            totalBounty='$29,000 USD and 24 ETH'
          >
            We are interested in how resistant the Legendre pseudo-random function is to key
            recovery attacks, as well as any other interesting results on the Legendre PRF.
          </BountyCard>

          <BountyCard
            url={MIMC_HASH_BOUNTIES_URL}
            title='MiMC Hash Challenge'
            postedBy='Ethereum Foundation and Protocol Labs'
            totalBounty='$20,000 USD per challenge'
          >
            The Ethereum Foundation and Protocol Labs are offering rewards for finding collisions in
            MiMCSponge, a sponge construction instantiated with MiMC-Feistel over a prime field,
            targeting 128-bit and 80-bit security, on one of two fields described below.
          </BountyCard>

          <BountyCard
            url={ZK_HASH_BOUNTIES_URL}
            title='ZK Hash Function Cryptanalysis Bounties'
            postedBy='Ethereum Foundation'
            totalBounty='$200,000 USD'
          >
            Help us understand the security of new hash functions better.
          </BountyCard>
        </Stack>
      </main>
    </>
  );
};

export default Bounties;

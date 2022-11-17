import { Heading, Link, Stack, Text } from '@chakra-ui/react';
import type { NextPage } from 'next';

import { PageMetadata } from '../components/UI';

const Team: NextPage = () => {
  return (
    <>
      <PageMetadata
        title='Team'
        description='About the team behind cryptography research at the Ethereum Foundation.'
      />

      <main>
        <Heading as='h1' mb={10}>
          Team
        </Heading>

        <Text mb={12}>
          Meet our team of world leading cryptography researchers. It goes without saying that we
          are all interested in cryptography and blockchains. We also have more specific interests
          ranging from cryptanalysis to zero-knowledge proofs to post-quantum cryptography.
        </Text>

        <Stack spacing={5}>
          <Stack>
            <Text>
              <Link
                href='https://twitter.com/drakefjustin'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Justin Drake.</strong>
              </Link>{' '}
              MEV; secret leader election; verifiable delay functions; zkEVM; sharding; and
              proof-of-custody.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://dankradfeist.de/about/'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Dankrad Feist.</strong>
              </Link>{' '}
              Vector commitments; Verkle trees; MPCs; and zero-knowledge proofs.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://dblp.org/pid/47/11389.html'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Gottfried Herold.</strong>
              </Link>{' '}
              Public key cryptanalysis.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://github.com/asn-d6'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>George Kadianakis.</strong>
              </Link>{' '}
              Shuffling ZKPs; polynomial commitments; protocol design and implementation.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://www.khovratovich.info/'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Dmitry Khovratovich.</strong>
              </Link>{' '}
              Symmetric crypto design; cryptanalysis of schemes and protocols; zero-knowledge proofs
              and circuits; verifiable delay functions; and privacy and anonymity.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://www.marymaller.com/'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Mary Maller.</strong>
              </Link>{' '}
              Zero-knowledge proofs; distributed key generation; and setup ceremonies.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://msimkin.github.io/'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Mark Simkin.</strong>
              </Link>{' '}
              Cryptographic protocols and primitives; algorithms and data structures.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://www.intothesymmetry.com/'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Antonio Sanso.</strong>
              </Link>{' '}
              Isogenies; elliptic curves; public key cryptography; cryptanalysis.
            </Text>
          </Stack>

          <Stack>
            <Text>
              <Link
                href='https://zhenfeizhang.github.io/material/aboutme/'
                color='brand.lightblue'
                _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
                isExternal
              >
                <strong>Zhenfei Zhang.</strong>
              </Link>{' '}
              Lattice based cryptography; zero-knowledge proofs; cryptographic implementations.
            </Text>
          </Stack>
        </Stack>
      </main>
    </>
  );
};

export default Team;

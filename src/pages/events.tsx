import { Heading, Stack } from '@chakra-ui/react';
import type { NextPage } from 'next';

import { Event, PageMetadata } from '../components/UI';

const Events: NextPage = () => {
  return (
    <>
      <PageMetadata
        title='Events'
        description='View upcoming and past cryptography events in the Ethereum ecosystem.'
      />

      <main>
        <Heading as='h1' mb={10}>
          Events
        </Heading>

        <Stack mb={6} spacing={8}>
          <Event
            conference='Cryptographic Frontier 2022, Trondheim'
            workshop='Open Problems in Decentralized Computation at Eurocrypt 2022'
          >
            this workshop brings the most interesting and challenging open cryptographic questions
            that Ethereum, Filecoin and other blockchain systems face, to the attention of academia.
            We will cover a large spectrum of research topics, such as vector commitments, SNARKs,
            shuffles, authenticated data structures and more. We will start the day with an update
            on to the problems discussed at last year&apos;s workshop.
          </Event>

          <Event
            conference='Cryptographic Frontier 2021, Zagreb'
            workshop='Open Problems in Ethereum Research at Eurocrypt 2021'
          >
            this workshop brought the most interesting and challenging open cryptographic questions
            that Ethereum faces to the attention of academia. We covered a large spectrum of
            research topics, such as multisignatures, commitments, verifiable delay functions,
            secure computation, zk-friendly hash functions and more.
          </Event>
        </Stack>
      </main>
    </>
  );
};

export default Events;

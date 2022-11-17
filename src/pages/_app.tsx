import { ChakraProvider } from '@chakra-ui/react';
import type { AppProps } from 'next/app';
import Head from 'next/head';

import { Layout } from '../components/layout';

import '../styles/globals.css';
import '@fontsource/libre-franklin/200.css';
import '@fontsource/libre-franklin/300.css';
import '@fontsource/libre-franklin/400.css';
import '@fontsource/libre-franklin/700.css';

import 'katex/dist/katex.min.css'; // `rehype-katex` does not import the CSS for you
import 'focus-visible/dist/focus-visible';

import theme from '../theme';

import favicon from '../../public/images/favicon.png';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <link rel='icon' type='image/x-icon' href={favicon.src} />
        <meta name='viewport' content='width=device-width, initial-scale=1' />
      </Head>

      <ChakraProvider theme={theme}>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </ChakraProvider>
    </>
  );
}

export default MyApp;

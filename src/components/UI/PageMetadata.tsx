import { FC } from 'react';
import Head from 'next/head';

import { HEAD_TITLE_LONG, HEAD_TITLE_SHORT } from '../../constants';

interface Props {
  title: string;
  description?: string;
}

export const PageMetadata: FC<Props> = ({ title, description }) => {
  const HEAD_TITLE = title.length > 20 ? HEAD_TITLE_SHORT : HEAD_TITLE_LONG;

  return (
    <Head>
      <title>
        {title} | {HEAD_TITLE}
      </title>
      <meta name='title' content={`${title} | ${HEAD_TITLE}`} />
      <meta name='description' content={description} />
      <meta name='application-name' content={HEAD_TITLE} />
      <meta name='image' content='https://crypto.ethereum.org/images/ef-logo-bg-white.png' />
      {/* OpenGraph */}
      <meta property='og:title' content={`${title} | ${HEAD_TITLE}`} />
      <meta property='og:description' content={description} />
      <meta property='og:type' content='website' />
      <meta property='og:site_name' content={HEAD_TITLE}></meta>
      <meta property='og:url' content='https://crypto.ethereum.org/' />
      <meta property='og:image' content='https://crypto.ethereum.org/images/ef-logo-bg-white.png' />
      <meta
        property='og:image:url'
        content='https://crypto.ethereum.org/images/ef-logo-bg-white.png'
      />
      <meta
        property='og:image:secure_url'
        content='https://crypto.ethereum.org/images/ef-logo-bg-white.png'
      />
      <meta property='og:image:alt' content={HEAD_TITLE} />
      <meta property='og:image:type' content='image/png' />
      {/* Twitter */}
      <meta name='twitter:card' content='summary_large_image' />
      <meta property='twitter:url' content='https://crypto.ethereum.org/' />
      <meta name='twitter:creator' content='@ethdotorg' />
      <meta name='twitter:site' content='@ethdotorg' />
      <meta name='twitter:title' content={HEAD_TITLE} />
      <meta name='twitter:description' content={description} />
      <meta
        name='twitter:image'
        content='https://crypto.ethereum.org/images/ef-logo-bg-white.png'
      />
    </Head>
  );
};

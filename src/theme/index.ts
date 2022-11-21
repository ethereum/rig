import { extendTheme } from '@chakra-ui/react';

import { breakpoints, colors, fonts } from './foundations';

const overrides = {
  breakpoints,
  colors,
  fonts
};

export default extendTheme(overrides);

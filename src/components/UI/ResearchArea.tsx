import { Heading, Stack, StackProps } from '@chakra-ui/react';
import { FC } from 'react';

interface Props {
  subtitle: string;
}

export const ResearchArea: FC<Props & StackProps> = ({ subtitle, children, ...props }) => {
  return (
    <Stack {...props}>
      <Heading as='h2' fontSize='3xl' fontWeight={600} mb={2}>
        {subtitle}
      </Heading>

      <Stack spacing={6}>{children}</Stack>
    </Stack>
  );
};

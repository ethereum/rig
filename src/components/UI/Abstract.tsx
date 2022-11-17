import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Text
} from '@chakra-ui/react';
import { FC } from 'react';

export const Abstract: FC = ({ children }) => {
  return (
    <Accordion allowToggle>
      <AccordionItem border='none'>
        <h2>
          <AccordionButton pl={0}>
            <AccordionIcon color='gray.600' fontSize='sm' />
            <Text color='gray.600' fontSize='sm'>
              Abstract
            </Text>
          </AccordionButton>
        </h2>
        <AccordionPanel pl={0}>{children}</AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
};

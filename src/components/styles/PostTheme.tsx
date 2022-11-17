import {
  Heading,
  Image,
  Link,
  ListItem,
  OrderedList,
  Stack,
  Table,
  TableContainer,
  Text,
  UnorderedList
} from '@chakra-ui/react';

export const PostTheme = {
  h1: ({ children }: any) => {
    return (
      <Heading as='h1' display='none'>
        {children}
      </Heading>
    );
  },
  h2: ({ children }: any) => {
    return (
      <Heading as='h2' fontSize='3xl' fontWeight={600} mt={10} mb={5}>
        {children}
      </Heading>
    );
  },
  h3: ({ children }: any) => {
    return (
      <Heading as='h3' fontSize='2xl' fontWeight={600} mt={10} mb={5}>
        {children}
      </Heading>
    );
  },
  h4: ({ children }: any) => {
    return (
      <Heading as='h4' fontSize='xl' fontWeight={600} mt={10} mb={5}>
        {children}
      </Heading>
    );
  },
  p: ({ children }: any) => {
    return (
      <Text mb={4} fontSize='md'>
        {children}
      </Text>
    );
  },
  ol: ({ children }: any) => {
    return (
      <OrderedList ml={8} mt={2} mb={10}>
        {children}
      </OrderedList>
    );
  },
  ul: ({ children }: any) => {
    return (
      <UnorderedList ml={8} mt={2} mb={10}>
        {children}
      </UnorderedList>
    );
  },
  li: ({ children, id }: any) => {
    return <ListItem id={id}>{children}</ListItem>;
  },
  a: ({ children, href }: any) => {
    return (
      <Link
        textDecoration='none'
        color='brand.lightblue'
        _hover={{ color: 'brand.orange', textDecoration: 'underline' }}
        href={href}
        isExternal={href.startsWith('http') ? true : false}
      >
        {children}
      </Link>
    );
  },
  img: (img: any) => {
    return (
      <Stack my={12} alignItems='center'>
        <Image src={img.src} alt={img.alt} maxW={{ base: '100%', md: '70%' }} h='auto' />
      </Stack>
    );
  },
  pre: ({ children }: any) => {
    return (
      <Stack my={4}>
        <pre>{children}</pre>
      </Stack>
    );
  },
  code: (code: any) => {
    return (
      <Text
        as={!!code.inline ? 'span' : 'p'}
        px='4px'
        py='2px'
        color='#c7254e'
        bg='#f9f2f4'
        borderRadius={3}
        fontFamily='Menlo,Monaco,Consolas,"Courier New",monospace'
        fontSize='sm'
        whiteSpace='pre-wrap'
      >
        {code.children[0]}
      </Text>
    );
  },
  table: ({ children }: any) => {
    return (
      <TableContainer my={10} border='1px solid #EDF2F7' borderRadius='md'>
        <Table variant='simple'>{children}</Table>
      </TableContainer>
    );
  }
};

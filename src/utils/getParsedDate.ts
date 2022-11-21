export const getParsedDate = (date: string) => {
  const dateOptions = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' } as const;

  return new Date(date).toLocaleDateString('en-US', dateOptions);
};

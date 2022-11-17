export const sortByDate = (a: JSX.Element, b: JSX.Element) => {
  if (a.props.date < b.props.date) {
    return 1;
  }
  if (a.props.date > b.props.date) {
    return -1;
  }

  return 0;
};

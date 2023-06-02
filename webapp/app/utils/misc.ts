export const mapValuesToOptions = (values: string[]) => {
  return values.map((value) => ({
    label: value,
    value,
  }));
};

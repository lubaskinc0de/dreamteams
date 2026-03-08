export const combineDateTime = (date: any, time: any): string => {
  if (!date) return '';
  const hour = time?.hour ?? 0;
  const minute = time?.minute ?? 0;
  return new Date(date.year, date.month - 1, date.day, hour, minute).toISOString();
};

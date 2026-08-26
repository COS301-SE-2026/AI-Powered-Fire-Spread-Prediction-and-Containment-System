export function FormatDate(isoString: string): string {
  const date = new Date(isoString);
  const datePart = date.toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    timeZone: 'Africa/Johannesburg',
  });
  const timePart = date.toLocaleTimeString('en-ZA', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Africa/Johannesburg',
  });
  return `${datePart} | ${timePart}`;
}

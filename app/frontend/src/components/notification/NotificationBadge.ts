export type BadgeStyle = {
  bg?: string;
  text?: string;
  border?: string;
};

export const SeverityBadge: Record<string, BadgeStyle> = {
  low: { bg: 'bg-secondary/10', text: 'text-secondary', border: 'border-secondary' },
  moderate: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/25' },
  high: { bg: 'bg-primary/10', text: 'text-primary', border: 'border-primary/25' },
  extreme: { bg: 'bg-error/10', text: 'text-error', border: 'border-error/25' },
};

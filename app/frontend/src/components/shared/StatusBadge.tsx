import React from 'react';

export type BadgeStyle = {
    bg?: string;
    text?: string;
    border?: string;
}

interface StatusBadgeProps {
    readonly label: string;
    readonly style: BadgeStyle;
}

export function StatusBadge({ label, style }: StatusBadgeProps) {
  const { bg = 'bg-carbon-card', text = 'text-text-primary/50', border = '' } = style;

  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${bg} ${text} ${border}`}>
      {label}
    </span>
  );
}

import React from 'react';

export type BadgeState = 'pending' | 'verified' | 'rejected' | 'offline' | 'active';

interface BadgeProps {
  label: string;
  state: BadgeState;
}

const stateClasses: Record<BadgeState, string> = {
  pending:  'badge-warning',
  verified: 'badge-success',
  active:   'badge-primary',
  rejected: 'badge-error',
  offline:  'badge-ghost',
};

export default function Badge({ label, state }: BadgeProps): React.JSX.Element {
  return (
    <span className={`badge badge-soft badge-sm font-mono text-[9px] uppercase tracking-widest rounded-[2px] ${stateClasses[state]}`}>
      {label}
    </span>
  );
}
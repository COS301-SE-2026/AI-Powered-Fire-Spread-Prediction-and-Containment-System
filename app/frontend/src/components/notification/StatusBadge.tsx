import React from 'react';
import { SeverityBadge } from './NotificationBadge';
import { FireNotification } from '../../types/Notifications';

interface NotificationBadgeProps {
  readonly severity: FireNotification['severity'];
}

export function NotificationBadge({ severity }: NotificationBadgeProps) {
  const {
    bg = 'bg-carbon-card',
    text = 'text-text-primary/50',
    border = '',
  } = SeverityBadge[severity] ?? {};

  return (
    <span
      className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${bg} ${text} ${border}`}
    >
      {severity}
    </span>
  );
}

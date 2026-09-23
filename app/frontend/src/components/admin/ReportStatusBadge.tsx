import React from 'react';
import { StatusBadge, type BadgeStyle } from '../shared/StatusBadge';
import type { ReportStatus } from '../../types/Report';

const reportStatusColors: Record<string, BadgeStyle> = {
  pending: { bg: 'bg-torch/10', text: 'text-torch', border: 'border-torch/25' },
  approved: { bg: 'bg-humidity/10', text: 'text-humidity', border: 'border-humidity/25' },
  rejected: { bg: 'bg-flare/10', text: 'text-flare', border: 'border-flare/25' },
  revoked: { bg: 'bg-ignite/20', text: 'text-ignite', border: 'border-ignite/50' },
  verified: { bg: 'bg-humidity/10', text: 'text-humidity', border: 'border-humidity/25' },
  none: {},
};

interface ReportStatusBadgeProps {
  readonly status: ReportStatus;
}

export function ReportStatusBadge({ status }: ReportStatusBadgeProps) {
  const displayStatus = status === 'received' ? 'pending' : status;
  return <StatusBadge label={displayStatus} style={reportStatusColors[displayStatus] ?? {}} />;
}

import React from 'react';
import { StatusBadge, type BadgeStyle } from '../shared/StatusBadge';
import type { Status } from '../../types/GPUWorkers';

const gpuStatusColors: Record<string, BadgeStyle> = {
  active: { bg: 'bg-humidity/10', text: 'text-humidity', border: 'border-humidity/25' },
  busy: { bg: 'bg-wind/10', text: 'text-wind', border: 'border-wind/25' },
  offline: { bg: 'bg-carbon-card', text: 'text-text-muted', border: 'border-carbon-stroke' },
  rejected: { bg: 'bg-ignite/10', text: 'text-ignite', border: 'border-ignite/25' },
  quarantined: { bg: 'bg-torch/10', text: 'text-torch', border: 'border-torch/25' },
  deactivated: { bg: 'bg-carbon-card', text: 'text-text-muted', border: 'border-carbon-stroke' },
  removed: { bg: 'bg-error/10', text: 'text-error', border: 'border-error/25' },
};

interface GpuStatusBadgeProps {
  readonly status: Status;
}

export function GpuStatusBadge({ status }: GpuStatusBadgeProps) {
  return <StatusBadge label={status} style={gpuStatusColors[status] ?? {}} />;
}

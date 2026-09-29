import React, { useState, useRef, useEffect } from 'react';
import { StatusBadge, type BadgeStyle } from '../shared/StatusBadge';
import type { GPUWorker, Status } from '../../types/GPUWorkers';
import { FormatDate } from '../../lib/FormatDate';

const gpuStatusColors: Record<string, BadgeStyle> = {
  active: { bg: 'bg-humidity/10', text: 'text-humidity', border: 'border-humidity/25' },
  busy: { bg: 'bg-wind/10', text: 'text-wind', border: 'border-wind/25' },
  offline: { bg: 'bg-carbon-card', text: 'text-text-muted', border: 'border-carbon-stroke' },
  rejected: { bg: 'bg-ignite/10', text: 'text-ignite', border: 'border-ignite/25' },
  quarantined: { bg: 'bg-torch/10', text: 'text-torch', border: 'border-torch/25' },
  deactivated: { bg: 'bg-carbon-card', text: 'text-text-muted', border: 'border-carbon-stroke' },
  removed: { bg: 'bg-error/10', text: 'text-error', border: 'border-error/25' },
};

interface MessageProps{
  title: string;
  body: string;
}

function getStatusMessage(worker: GPUWorker): MessageProps {
  if (worker.status === 'active') {
    return {
      title: worker.activated_at ? `Active since ${FormatDate(worker.activated_at)}` : 'Active',
      body: 'Connected and ready for jobs.',
    };
  }
  if (worker.status === 'busy') {
    return {
      title: 'Currently processing',
      body: 'This worker is running a job right now.',
    };
  }
  if (worker.status === 'offline') {
    return {
      title: worker.last_heartbeat ? `Last seen ${FormatDate(worker.last_heartbeat)}` : 'Never connected',
      body: 'No heartbeat received recently',
    };
  }
  if (worker.status === 'quarantined') {
    return {
      title: 'Flagged for review',
      body: 'This machine failed a validation check and is pending review.',
    };
  }
  if (worker.status === 'deactivated') {
    return {
      title: worker.deactivated_at ? `Deactivated ${FormatDate(worker.deactivated_at)}` : 'Deactivated',
      body: 'Manually paused. Reactivate to resume accepting jobs.',
    };
  }
  if (worker.status === 'rejected') {
    return {
      title: 'Rejected',
      body: 'This node did not pass verification and was never activated.',
    };
  }
  return {
    title: worker.removed_at ? `Removed ${FormatDate(worker.removed_at)}` : 'Removed',
    body: worker.removal_reason ? worker.removal_reason : 'No reason provided.',
  };
}

interface GpuStatusBadgeProps {
  readonly worker: GPUWorker;
}

export function GpuStatusBadge({ worker }: GpuStatusBadgeProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const style = gpuStatusColors[worker.status] ?? {};
  const { title, body } = getStatusMessage(worker);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)){
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);

  return (
    <div className='relative inline-block' ref={containerRef}>
      <button type='button' onClick={() => setOpen((prev) => !prev)} className='cursor-pointer'>
        <StatusBadge label={worker.status} style={style} />
      </button>
      {open && (
        <div role='tooltip' className={`absolute z-50 mt-2 w-64 rounded-lg border bg-carbon-side p-3 shadow-lg ${style.border} ${style.text}`}>
          <p className='text-sm font-semibold'>{title}</p>
          <p className='text-xs mt-1 text-text-muted'>{body}</p>
        </div>
      )}
    </div>
  );
}

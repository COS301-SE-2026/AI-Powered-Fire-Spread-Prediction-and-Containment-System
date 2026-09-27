import React, { useState } from 'react';
import { GPUWorker, Status} from '../../types/GPUWorkers';
import { FormatDate } from '../../lib/FormatDate';
import { GpuStatusBadge } from './GpuStatusBadge';
import { RemoveModal } from './Remove';
import { WorkerActions } from './WorkerActions';

interface GpuWorkersTableProps {
  readonly workers: GPUWorker[];
  readonly filter: 'All' | Status;
  readonly variant: 'admin' | 'volunteer';
  readonly onActivate: (id: string) => void;
  readonly onDeactivate: (id: string) => void;
  readonly onRemove: (id: string, reason: string) => void;
}

function formatVram(vramMb: number): string {
    return `${Number((vramMb / 1024).toFixed(1))} GB`
}

export function GpuWorkersTable({ workers, filter, variant,onActivate, onDeactivate, onRemove }: GpuWorkersTableProps) {
  const [pendingRemoval, setPendingRemoval] = useState<GPUWorker | null>(null);
  const filtered = workers
    .filter((w) => filter === 'All' || w.status === filter)
    .sort((a, b) => new Date(b.activated_at).getTime() - new Date(a.activated_at).getTime());

  const isAdmin = variant === 'admin';
  const columnCount = isAdmin ? 8 : 6;

  return (
    <>
    <div className="w-full overflow-x-auto rounded-2xl border border-carbon-stroke">
      <table className="table table-pin-rows w-full">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
              Label
            </th>
            {isAdmin && (
              <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
                Worker ID
              </th>
            )}
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
              GPU hardware
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
              VRAM
            </th>
            {isAdmin && (
              <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
                User contact
              </th>
            )}
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
              Status
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
              Last active
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-10 py-3">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan={columnCount} className="px-12 py-8 text-center text-sm font-bold text-error">
                No GPU workers found
              </td>
            </tr>
          ) : (
            filtered.map((worker) => (
              <tr
                key={worker.id}
                className="[&>td]:border-t [&>td]:border-carbon-card hover:bg-surface-hover"
              >
                <td className="px-10 py-3 text-sm text-text-primary">{worker.label}</td>
                {isAdmin && (
                  <td className="px-10 py-3 text-sm text-text-primary">{worker.id}</td>
                )}
                <td className="px-10 py-3 text-sm text-text-primary">{worker.gpu_name}</td>
                <td className="px-10 py-3 text-sm text-text-primary">{formatVram(worker.vram_mb)}</td>
                {isAdmin && (
                  <td className="px-10 py-3 text-sm text-text-primary">{worker.user_id}</td>
                )}
                <td className="px-10 py-3 text-sm text-text-primary">
                  <GpuStatusBadge worker={worker} />
                </td>
                <td className="px-10 py-3 text-sm text-text-primary">
                  {worker.last_heartbeat === null ? 'Never' : FormatDate(worker.last_heartbeat)}
                </td>
                <td className="px-10 py-3">
                  <WorkerActions worker={worker} onActivate={onActivate} onDeactivate={onDeactivate} onRemove={setPendingRemoval} />
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
    {pendingRemoval && (
        <RemoveModal
          worker={pendingRemoval}
          variant={variant}
          onClose={() => setPendingRemoval(null)}
          onSubmit={(id, reason) => {
            onRemove(id, reason);
            setPendingRemoval(null);
          }}
        />
      )}
  </>
  );
}

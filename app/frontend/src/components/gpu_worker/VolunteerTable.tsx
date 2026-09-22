import React from 'react';
import { useRouter } from 'next/router';
import { GPUWorker, Status} from '../../types/GPUWorkers';
import { FormatDate } from '../../lib/FormatDate';
import { GpuStatusBadge } from './GpuStatusBadge';

interface GpuWorkersTableProps {
  readonly workers: GPUWorker[];
  readonly filter: 'All' | Status;
  readonly onDeactivate: (id: string) => void;
  readonly onRemove: (id: string) => void;
}

function formatVram(vramMb: number): string {
    return `${Number((vramMb / 1024).toFixed(1))} GB`
}

export function FireReportsTable({ workers, filter, onDeactivate, onRemove }: GpuWorkersTableProps) {
  const filtered = workers
    .filter((r) => filter === 'All' || r.status === filter)
    .sort((a, b) => new Date(b.activated_at).getTime() - new Date(a.activated_at).getTime());

  const router = useRouter();

  return (
    <div className="w-full overflow-x-auto rounded-2xl border border-carbon-stroke">
      <table className="table table-pin-rows w-full">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Label
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              GPU hardware
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              VRAM (MB)
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Status
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Last active
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan={8} className="px-4 py-8 text-center text-sm font-bold text-error">
                No GPU workers found
              </td>
            </tr>
          ) : (
            filtered.map((worker) => (
              <tr
                key={worker.id}
                className="[&>td]:border-t [&>td]:border-carbon-card hover:bg-surface-hover even:bg-carbon-bg/80"
              >
                <td className="px-4 text-sm text-text-primary">{worker.label}</td>
                <td className="px-4 text-sm text-text-primary">{worker.gpu_name}</td>
                <td className="px-4 text-sm text-text-primary">{formatVram(worker.vram_mb)}</td>
                <td className="px-4 text-sm text-text-primary">
                  <GpuStatusBadge status={worker.status} />
                </td>
                <td className="px-4 text-sm text-text-primary">
                  {worker.last_heartbeat === null ? 'Never' : FormatDate(worker.last_heartbeat)}
                </td>
                <td className="px-4 py-3">
                    <div className='flex gap-2'>
                        <button
                            type="button"
                            onClick={() => onDeactivate(worker.id)}
                            className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors"
                        >
                            Deactivate
                        </button>
                        <button
                            type="button"
                            onClick={() => onRemove(worker.id)}
                            className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors"
                        >
                            Remove
                        </button>
                    </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

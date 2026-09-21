import { ChevronRight } from 'lucide-react';
import type { NearbyResource } from '../../hooks/useNearbyResources';
import { STATUS_LABEL, resourceLabel, capacityLabel } from '../../lib/ResourceLabels';
import type { Status } from '../../types/Resource';

const STATUS_BADGE: Record<Status, { label: string; className: string }> = {
    available:   { label: 'Available',   className: 'bg-succes/15 text-success border-succes/40' },
    dispatched:  { label: 'Dispatched',  className: 'bg-primary/15 text-primary border-primary/40' },
    unavailable: { label: 'Unavailable', className: 'bg-carbon-stroke/40 text-text-muted border-carbon-stroke' },
}

interface NearbyResourceList {
  readonly resources: NearbyResource[];
  readonly selectedResourceId?: string | null;
  readonly onSelectResource?: (r: NearbyResource) => void;
}

export function NearbyResources({ resources, selectedResourceId = null, onSelectResource = undefined }: NearbyResourceList) {
  if (resources.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <p className="text-xs opacity-50">No nearby fires</p>
      </div>
    );
  }
  return (
    <div className="flex flex-col p-2">
      {resources.map((r) => {
        const badge = STATUS_BADGE[r.status];
        return (
          <button
            key={r.id}
            onClick={() => onSelectResource?.(r)}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors ${r.id === selectedResourceId ? 'bg-carbon-card/70 border-ignite' : '' }`}>
            <div className="flex-1 min-w-0 text-center">
                <p className="font-semibold text-medium">{resourceLabel(r)} · {capacityLabel(r)}</p>
                <p className="text-sm text-text-muted">
                    {r.distance.toFixed(1)} km · {r.location}
                </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
                <span className={`whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-semibold ${badge.className}`}>
                    {badge.label}
                </span>
                <ChevronRight className="size-4 opacity-30" />
            </div>
          </button>
        );
    })}
    </div>
  );
}

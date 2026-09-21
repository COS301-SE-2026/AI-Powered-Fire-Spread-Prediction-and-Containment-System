import { ChevronRight } from 'lucide-react';
import type { NearbyResource } from '../../hooks/useNearbyResources';
import { STATUS_LABEL, resourceLabel, capacityLabel } from '../../lib/resourceLabels';


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
    <div className="h-194 overflow-y-auto flex flex-col p-2">
      {resources.map((r) => {
        const status = STATUS_LABEL[r.status];
        return (
          <button
            key={r.id}
            onClick={() => onSelectResource?.(r)}
            className={`flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors ${r.id === selectedResourceId ? 'bg-carbon-card/70 border-ignite' : '' }`}>
            <div>
              <p className="font-semibold text-medium">{resourceLabel(r)} · {capacityLabel(r)}</p>
              <p className="text-sm text-text-muted">
                {r.distance.toFixed(1)} km · {r.location}
              </p>
              <p className={`text-xs font-semibold ${status.className}`}>{status.label}</p>
            </div>

            <div className="flex items-center gap-2">
              <ChevronRight className="size-4 opacity-30" />
            </div>
          </button>
        );
    })}
    </div>
  );
}

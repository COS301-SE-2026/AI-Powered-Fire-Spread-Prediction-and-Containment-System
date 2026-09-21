import { ChevronRight } from 'lucide-react';
import type { NearbyResource } from '../../hooks/useNearbyResources';
import { resourceLabel, capacityLabel } from '../../lib/ResourceLabels';
import { RESOURCE_GROUPS, GROUP_BY_RESOURCE } from '../../lib/ResourceGroups';


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
        const group = RESOURCE_GROUPS[GROUP_BY_RESOURCE[r.resource]];
        const Icon = group.icon;
        return (
          <button
            key={r.id}
            onClick={() => onSelectResource?.(r)}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors ${r.id === selectedResourceId ? 'bg-carbon-card/70 border-ignite' : '' }`}>
            <span className='flex size-9 shrink-0 items-center justify-center rounded-lg' style={{ background: group.color}}>
                <Icon className='size-5 text-carbon-bg' />
            </span>
            <div className="flex-1 min-w-0 text-center">
                <p className="font-semibold text-medium">{resourceLabel(r)} · {capacityLabel(r)}</p>
                <p className="text-sm text-text-muted">
                    {r.distance.toFixed(1)} km · {r.location}
                </p>
            </div>
            <ChevronRight className="size-4 opacity-30" />
          </button>
        );
    })}
    </div>
  );
}

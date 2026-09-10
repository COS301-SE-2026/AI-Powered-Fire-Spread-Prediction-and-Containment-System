import { ChevronRight } from 'lucide-react';
import { statusBadge } from '../admin/statusBadge';
import type { NearbyFire } from '../../types/FirefighterDashboard';

interface NearbyFireReports {
  readonly nearbyFires: NearbyFire[];
  readonly selectedFireId?: string | null;
  readonly onSelectFire?: (ref: string) => void;
}

export function NearbyReports({ nearbyFires, selectedFireId = null, onSelectFire = undefined }: NearbyFireReports) {
  const fires = (nearbyFires ?? []).filter((f) => f.status?.toLowerCase() === 'verified');

  if (fires.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <p className="text-xs opacity-50">No nearby fires</p>
      </div>
    );
  }
  return (
    <div className="h-194 overflow-y-auto flex flex-col p-2">
      {fires.map((fire) => (
          <button
            key={fire.location_text}
            onClick={() => onSelectFire?.(fire.location_text)}
            className={`flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors ${fire.location_text === selectedFireId ? 'bg-carbon-card/70 border-ignite' : '' }`}>
            <div>
              <p className="font-semibold text-medium">{fire.location_text}</p>
              <p className="text-sm text-text-muted">
                {fire.distance} km · {fire.time_ago}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <ChevronRight className="size-4 opacity-30" />
            </div>
          </button>
        ))}
    </div>
  );
}

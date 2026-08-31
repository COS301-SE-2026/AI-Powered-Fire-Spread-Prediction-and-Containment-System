import { ChevronRight } from 'lucide-react';
import { NearbyFire } from '../../types/FirefighterDashboard';

interface NearbyFireReports {
  readonly nearbyFires: NearbyFire[];
}

const statusColor = (s: string) =>
  ({
    verified: 'bg-ignite/20 text-flare border border-ignite/40',
    pending: 'bg-torch/20 text-torch border border-torch/35',
    received: 'bg-humidity/20 text-humidity border border-humidity/35',
  })[s] ?? 'bg-carbon-card text-text-primary/50';

export function NearbyReports({ nearbyFires }: NearbyFireReports) {
  const fires = nearbyFires ?? [];

  if (fires.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <p className="text-xs opacity-50">No nearby fires</p>
      </div>
    );
  }
  return (
    <div className="h-full overflow-y-auto flex flex-col p-2">
      {nearbyFires.map((fire, i) => (
        <div
          key={i}
          className="flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors"
        >
          <div>
            <p className="font-semibold text-sm">{fire.location_text}</p>
            <p className="text-xs opacity-50">
              {fire.distance} km · {fire.time_ago}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className={`badge px-3 py-1 rounded-full ${statusColor(fire.status)}`}>
              {fire.status}
            </span>
            <ChevronRight className="size-4 opacity-30" />
          </div>
        </div>
      ))}
    </div>
  );
}

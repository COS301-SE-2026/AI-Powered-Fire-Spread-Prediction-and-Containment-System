import { NearbyFire } from '../../types/FirefighterDashboard';

interface NearbyFireReports {
  readonly nearbyFires: NearbyFire[];
}

export function MapStatsOverlay({ nearbyFires }: NearbyFireReports) {
  if (nearbyFires.length === 0) {
    return (
      <div className="absolute top-14 md:top-16 left-2 md:left-4 z-10 flex flex-col gap-1 md:gap-2">
        {/* Active fires */}
        <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-3 py-2 md:px-4 md:py-3 flex flex-col">
          <span className="text-xs md:text-sm font-bold tracking-widest text-text-muted uppercase">
            Active Fires
          </span>
          <span className="text-lg md:text-2xl font-display font-bold text-ignite">0</span>
          <span className="text-xs md:text-sm text-text-muted">in your area</span>
        </div>

        {/* Nearest Fire */}
        <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-3 py-2 md:px-4 md:py-3 flex flex-col">
          <span className="text-xs md:text-sm font-bold tracking-widest text-text-muted uppercase">
            Nearest
          </span>
          <span className="text-lg md:text-2xl font-display font-bold text-ignite">-</span>
          <span className="text-xs md:text-sm text-text-muted">away</span>
        </div>

        {/* Pending/Unverified */}
        <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
          <span className="text-sm font-bold tracking-widest text-text-muted uppercase">
            Unverified Reports
          </span>
          <span className="text-2xl font-display font-bold text-ignite">0</span>
          <span className="text-sm text-text-muted">Unverified</span>
        </div>
      </div>
    );
  }

  const activeFires = nearbyFires.filter((fire) => fire.status === 'verified').length;
  const unverifiedFires = nearbyFires.filter(
    (fire) => fire.status === 'pending' || fire.status === 'received'
  ).length;
  const nearestFire = nearbyFires[0].distance;

  return (
    <div className="absolute top-16 left-4 z-10 flex flex-col gap-2">
      {/* Active fires */}
      <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-3 py-2 md:px-4 md:py-3 flex flex-col">
          <span className="text-xs md:text-sm font-bold tracking-widest text-text-muted uppercase">
            Active Fires
          </span>
          <span className="text-lg md:text-2xl font-display font-bold text-ignite">{activeFires}</span>
          <span className="text-xs md:text-sm text-text-muted">in your area</span>
        </div>

      {/* Nearest Fire */}
      <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-3 py-2 md:px-4 md:py-3 flex flex-col">
          <span className="text-xs md:text-sm font-bold tracking-widest text-text-muted uppercase">
            Nearest
          </span>
          <span className="text-lg md:text-2xl font-display font-bold text-ignite">{nearestFire} km</span>
          <span className="text-xs md:text-sm text-text-muted">away</span>
        </div>

      {/* Pending/Unverified */}
      <div className="bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col">
          <span className="text-sm font-bold tracking-widest text-text-muted uppercase">
            Unverified Reports
          </span>
          <span className="text-2xl font-display font-bold text-ignite">{unverifiedFires}</span>
          <span className="text-sm text-text-muted">Unverified</span>
        </div>
    </div>
  );
}

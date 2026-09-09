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
      </div>
    );
  }

  const verified = nearbyFires.filter((fire) => fire.status === 'verified');
  const activeFires = verified.length;
  const nearestFire = verified.length ? Math.min(...verified.map((f) => f.distance)) : null;

  return (
    <div className="absolute top-14 md:top-16 left-2 md:left-4 z-10 flex flex-col gap-1 md:gap-2">
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
          <span className="text-lg md:text-2xl font-display font-bold text-ignite">{nearestFire !== null ? `${nearestFire} km` : '-'}</span>
          <span className="text-xs md:text-sm text-text-muted">away</span>
        </div>
    </div>
  );
}

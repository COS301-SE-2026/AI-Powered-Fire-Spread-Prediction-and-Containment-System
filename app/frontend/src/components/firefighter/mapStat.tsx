import { Flame } from 'lucide-react';
import { NearbyFire } from '../../types/FirefighterDashboard';

interface NearbyFireReports {
  readonly nearbyFires: NearbyFire[];
  readonly positionClass?: string;
}

export function MapStatsOverlay({ nearbyFires, positionClass = 'top-14 md:top-16 left-2 md:left-4' }: NearbyFireReports) {
  const verified = nearbyFires.filter((fire) => fire.status === 'verified');
  const activeFires = verified.length;
  const nearestFire = verified.length ? Math.min(...verified.map((f) => f.distance)) : null;
  const nearestText = nearestFire !== null ? `${nearestFire}` : '-';

  return (
    <div className={`absolute ${positionClass} z-10`}>
      {/* PWA */}
      <div className='md:hidden flex items-center gap-2 rounded-full border border-carbon-card bg-carbon-gb/80 backdrop-blur-md px-3 py-1.5 text-xs text-text-muted shadow-lg'>
          <Flame className='w-3.5 h-3.5 text-ignite shrink-0' />
          <span>
            <span className='font-bold text-ignite'>{activeFires}</span> active
          </span>
          <span>
            <span className='opacity-40'>|</span>
          </span>
          <span>
            <span className='font-bold text-ignite'>{nearestText}</span> nearest
          </span>
        </div>
      
      <div className='hidden md:flex flex-col gap-2'>
        {/* Active fires */}
        <div className='bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col'>
          <span className='text-sm font-bold tracking-widest text-text-muted uppercase'>
            Active Fires
          </span>
          <span className='text-2xl font-display font-bold text-ignite'>{activeFires}</span>
          <span className='text-sm text-text-muted'>in your area</span>
        </div>
        {/* Nearest Fire */}
          <div className='bg-carbon-bg/80 backdrop-blur-md border border-carbon-card rounded-xl px-4 py-3 flex flex-col'>
            <span className='text-sm font-bold tracking-widest text-text-muted uppercase'>
              Nearest
            </span>
            <span className='text-2xl font-display font-bold text-ignite'>{nearestFire !== null ? `${nearestFire} km` : '-'}</span>
            <span className='text-sm text-text-muted'>away</span>
          </div>
        </div>
    </div>
  );
}

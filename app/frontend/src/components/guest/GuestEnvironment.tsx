import React from 'react';
import { Thermometer, Wind, Droplets, Flame } from 'lucide-react';
import type { EnvironmentVariables } from '../../types/FirefighterDashboard';
import { StatCard } from './GuestStatCard';

export function GuestEnvironment({ data }: { readonly data: EnvironmentVariables | null }) {
  if (!data) return <div className="text-xs opacity-50">No environment data</div>;

  const { temperature, humidity, wind, wind_dir: windDeg, fire_danger: fireDanger, fdi } = data;

  function formatBand(band: string): string {
    return band.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
  }

  const windDir = (deg?: number) => {
    if (deg === undefined || deg === null) return 'N/A';
    const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    return dirs[Math.round(deg / 45) % 8];
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-1.5 sm:gap-2">
      <StatCard
        label="Temperature"
        value={temperature !== undefined ? `${temperature}°C` : '--'}
        icon={<Thermometer />}
      />
      <StatCard
        label="Humidity"
        value={humidity !== undefined ? `${humidity}%` : '--'}
        icon={<Droplets />}
      />
      <StatCard
        label="Wind"
        value={wind !== undefined ? `${wind} km/h ${windDir(windDeg)}` : '--'}
        icon={<Wind />}
      />
      <StatCard label={fdi !== undefined ? `Fire Danger (FDI ${fdi})` : 'Fire danger'} value={fireDanger ? formatBand(fireDanger) : '--'} icon={<Flame/>} />
    </div>
  );
}

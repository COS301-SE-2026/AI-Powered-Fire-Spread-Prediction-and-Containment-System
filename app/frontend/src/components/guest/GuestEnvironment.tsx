import React from 'react';
import { Thermometer, Wind, Droplets, Flame } from 'lucide-react';

interface EnvData {
  temperature?: number;
  humidity?: number;
  wind?: number;
  wind_dir?: number;
  fire_danger?: string;
}

export function GuestEnvironment({ data }: { data: EnvData | null }) {
  if (!data) return <div className="text-xs opacity-50">No environment data</div>;

  const { temperature, humidity, wind, wind_dir, fire_danger } = data;

  const windDir = (deg?: number) => {
    if (deg === undefined || deg === null) return 'N/A';
    const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    return dirs[Math.round(deg / 45) % 8];
  };

  return (
    <div className="grid grid-cols-2 gap-2">
      <StatCard label="Temperature" value={temperature !== undefined ? `${temperature}°C` : '--'} icon={<Thermometer />} />
      <StatCard label="Humidity" value={humidity !== undefined ? `${humidity}%` : '--'} icon={<Droplets />} />
      <StatCard label="Wind" value={wind !== undefined ? `${wind} km/h ${windDir(wind_dir)}` : '--'} icon={<Wind />} />
      <StatCard label="Fire Danger" value={fire_danger || '--'} icon={<Flame />} />
    </div>
  );
}

function StatCard({ label, value, icon }: any) {
  return (
    <div className="flex items-center gap-2 p-3 rounded-lg bg-carbon-side/60 border border-carbon-stroke">
      <div className="text-ignite">{icon}</div>
      <div>
        <div className="text-sm font-bold">{value}</div>
        <div className="text-xs opacity-50">{label}</div>
      </div>
    </div>
  );
}
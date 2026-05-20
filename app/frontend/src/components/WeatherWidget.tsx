import React, { ReactNode } from 'react';

type WeatherType = 'wind' | 'humidity' | 'danger' | 'temp';

interface WeatherWidgetProps {
  icon: ReactNode;
  value: string;
  label: string;
  type?: WeatherType;
}

const typeConfig: Record<WeatherType, { bg: string; accent: string }> = {
  wind:     { bg: 'rgba(55,138,221,0.08)',  accent: '#378ADD' },
  humidity: { bg: 'rgba(29,158,117,0.08)',  accent: '#1D9E75' },
  danger:   { bg: 'rgba(232,69,0,0.10)',    accent: '#E84500' },
  temp:     { bg: 'rgba(255,170,0,0.08)',   accent: '#FFAA00' },
};

export default function WeatherWidget({ icon, value, label, type = 'wind' }: WeatherWidgetProps) {
  const { bg, accent } = typeConfig[type];
  return (
    <div
      className="flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2.5 border-l-2 border-y-0 border-r-0"
      style={{ background: bg, borderColor: accent }}
    >
      <span className="shrink-0" style={{ color: accent }}>{icon}</span>
      <div className="min-w-0">
        <p className="font-mono text-sm font-semibold leading-none" style={{ color: accent }}>{value}</p>
        <p className="font-mono text-[10px] uppercase tracking-wider mt-1 truncate opacity-50" style={{ color: accent }}>{label}</p>
      </div>
    </div>
  );
}
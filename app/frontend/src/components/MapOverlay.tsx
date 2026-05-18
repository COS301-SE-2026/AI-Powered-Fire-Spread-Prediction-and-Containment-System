import React from 'react';

interface MapOverlayProps {
  label: string;
  count: string;
  subtext: string;
}

export default function MapOverlay({ label, count, subtext }: MapOverlayProps) {
  return (
    <div className="bg-[var(--color-carbon-card)]/80 backdrop-blur-sm border border-white/8 rounded-[var(--radius-md)] px-3 py-2 min-w-[160px]">
      <p className="font-mono text-[9px] uppercase tracking-widest text-white/35 leading-none">{label}</p>
      <p className="font-display font-bold text-xl text-white leading-tight mt-0.5">{count}</p>
      <p className="font-mono text-[9px] text-white/25 uppercase tracking-wider mt-0.5">{subtext}</p>
    </div>
  );
}
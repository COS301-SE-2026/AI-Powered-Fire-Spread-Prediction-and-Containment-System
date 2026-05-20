import React, { ReactNode } from 'react';

interface MapPopupProps {
  title: string;
  children: ReactNode;
  actions?: ReactNode;
}

export default function MapPopup({ title, children, actions }: MapPopupProps) {
  return (
    <div className="bg-[var(--color-carbon-card)]/90 backdrop-blur-md border border-white/8 rounded-[var(--radius-md)] p-4 w-64 shadow-xl">
      <div className="flex items-center gap-2 mb-3 pb-3 border-b border-white/8">
        <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-ignite)] animate-pulse shrink-0" />
        <h3 className="font-display font-bold text-sm uppercase tracking-wide text-white leading-none">{title}</h3>
      </div>
      <div className="space-y-1.5 font-mono text-[11px] text-white/40 mb-4">
        {children}
      </div>
      {actions && (
        <div className="flex gap-2 pt-3 border-t border-white/8">
          {actions}
        </div>
      )}
    </div>
  );
}
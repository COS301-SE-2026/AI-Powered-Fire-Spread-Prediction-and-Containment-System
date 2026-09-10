import React from 'react';

interface ActionCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick?: () => void;
}

export function ActionCard({ title, description, icon, onClick = undefined }: ActionCardProps) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-4 p-5 rounded-xl bg-carbon-side/60 backdrop-blur-sm border border-carbon-stroke hover:border-ignite hover:bg-smoke-hover active:scale-[0.98] transition-all text-left w-full h-full group"
    >
      {/* Icon wrapper */}
      <div className="size-10 rounded-lg bg-carbon-bg border border-carbon-card flex items-center justify-center text-text-primary/60 group-hover:text-ignite group-hover:border-ignite/30 transition-colors shrink-0">
        {icon}
      </div>

      {/* Text wrapper */}
      <div className="flex flex-col grid-rows-2 h-full">
        <span className="font-bold text-text-primary text-sm tracking-wide">{title}</span>
        <span className="text-xs text-text-muted font-medium mt-0.5">{description}</span>
      </div>
    </button>
  );
}

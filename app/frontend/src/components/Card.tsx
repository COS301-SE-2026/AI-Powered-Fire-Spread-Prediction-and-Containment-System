import React, { ReactNode } from 'react';

interface CardProps {
  title?: string;
  children: ReactNode;
  actions?: ReactNode; // A clean slot to inject multiple soft buttons
}

export default function Card({ title, children, actions }: CardProps) {
  return (
    <div className="card bg-base-100 border border-base-300 shadow-sm rounded-box overflow-hidden">
      <div className="card-body p-5 space-y-4">
        {title && (
          <h2 className="card-title text-sm font-bold border-b border-base-200 pb-2 tracking-tight">
            {title}
          </h2>
        )}
        <div className="flex-1 text-sm leading-relaxed">{children}</div>
        {actions && (
          <div className="card-actions justify-end gap-2 pt-2 border-t border-base-200/50">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
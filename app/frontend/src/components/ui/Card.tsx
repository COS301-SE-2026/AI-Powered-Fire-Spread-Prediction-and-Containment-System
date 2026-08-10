import React, { ReactNode } from 'react';

interface CardProps {
  title?: string;
  children: ReactNode;
  actions?: ReactNode;
}

export default function Card({ title, children, actions }: CardProps) {
  return (
    <div className="card bg-base-100 border border-base-100 shadow-sm rounded-box overflow-hidden">
      <div className="card-body p-5 space-y-4">
        {title && (
          <div className="border-b border-base-200/50 pb-2 mb-2 w-full">
            <h2 className="card-title text-sm text-slate-300 font-bold tracking-tight">
              {title}
            </h2>
          </div>
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
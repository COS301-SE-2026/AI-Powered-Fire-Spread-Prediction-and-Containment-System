import React from 'react';

interface CardProps {
  readonly title: string;
  readonly children: React.ReactNode;
}

export function Card({ title, children }: CardProps) {
  return (
    <div className="card bg-carbon-side/60 border border-carbon-card">
      <div className="card-body pt-3 mb-2">
        <h2>{title}</h2>
        {children}
      </div>
    </div>
  );
}

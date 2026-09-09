import React from 'react';

export interface MiniMetric {
  title: string;
  value: string;
  subtext: string;
  statusText?: string;
  icon: React.ReactNode;
}

interface SystemMetricsProps {
  metrics: MiniMetric[];
}

export const SystemMetrics: React.FC<SystemMetricsProps> = ({ metrics }) => (
  <section className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    {metrics.map((metric) => (
      <div
        key={metric.title}
        className="w-full h-full min-h-30 bg-base-200 border border-base-300 p-4 rounded shadow-sm flex flex-col justify-between "
      >
        <div className="flex items-center space-x-2 mb-2">
          <div className="tex-primary flex-shrink-0">{metric.icon}</div>

          <span className="text-medium font-bold text-text-muted uppercase tracking-wide font-display">
            {metric.title}
          </span>
        </div>
        <div>
          <span className="text-2xl font-normal text-base-content block mb-1 font-mono">
            {metric.value}
          </span>
          {metric.statusText ? (
            <span className="px-1.5 py-0.5 bg-success/10 text-success border border-success/30 text-[9px] font-bold rounded uppercase tracking-wide">
              {metric.statusText}
            </span>
          ) : (
            <span className="text-sm text-text-muted font-mono">{metric.subtext}</span>
          )}
        </div>
      </div>
    ))}
  </section>
);

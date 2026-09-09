import React from 'react';

interface DashboardMetricsProps {
  metrics: {
    active_fires: number;
    pending_approvals: number;
    total_users: number;
    system_status: string;
  };
}

export const DashboardMetrics: React.FC<DashboardMetricsProps> = ({ metrics }) => (
  <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl">
      <span className="text-medium font-semibold text-text-muted uppercase tracking-wider blocl mb-1.5">
        Active Fires
      </span>
      <div className="text-3xl font-extrabold text-red-500">{metrics.active_fires}</div>
    </div>

    <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl">
      <span className="text-medium font-semibold text-text-muted uppercase tracking-wider block mb-1">
        Pending Approvals
      </span>
      <div className="text-3xl font-extrabold text-primary">{metrics.pending_approvals}</div>
    </div>

    <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl">
      <span className="text-medium font-semibold text-text-muted uppercase tracking-wider block mb-1">
        Total Users
      </span>
      <div className="text-3xl font-extrabold text-white">{metrics.total_users}</div>
    </div>

    <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl">
      <span className="text-medium font-semibold text-text-muted uppercase tracking-wider block mb-1">
        System Status
      </span>
      <div className="text-3xl font-extrabold text-emerald-500 uppercase tracking-wide">
        {metrics.system_status}
      </div>
    </div>
  </section>
);

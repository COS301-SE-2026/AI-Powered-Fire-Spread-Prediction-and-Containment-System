// need to add sidebar still
import React, { useState, useEffect } from 'react';
import { LineChartIcon, DownloadCloudIcon, MicrochipIcon, HeartIcon } from 'lucide-react';
import { AdminSideBar } from '../../components/admin/AdminSideBar';
import { useAdminDashboard } from '../../hooks/useAdminDashboard';
import { PageHeader } from '../../components/layout/pageHeader';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';
import { DashboardMetrics } from '../../components/admin/adminDashboardMetrics';
import { SystemMetrics } from '../../components/admin/systemMetrics';
import { MiniMetric } from '../../types/AdminDashboard';

export const AdminDashBoardDetailed: React.FC = () => {
  const { topMetrics, activityLog, weeklyIncidents, systemMetrics, loading, error, isForbidden } =
    useAdminDashboard();

  if (loading) {
    return (
      <AdminSideBar hideLoginRegister>
        <div className="w-full min-h-screen flex items-center justify-center">
          <span className="loading loading-spinner loading-lg text-primary" />
        </div>
      </AdminSideBar>
    );
  }

  if (isForbidden) {
    return (
      <AdminSideBar hideLoginRegister>
        <div className="alert alert-error bg-red-900/20 border border-red-900 text-red-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      </AdminSideBar>
    );
  }

  const maxCount = Math.max(...weeklyIncidents.map((d) => d.count));

  if (error || !topMetrics || !systemMetrics) {
    return (
      <AdminSideBar hideLoginRegister>
        <div className="alert alert-error bg-error/50 border border-error text-text-error">
          <span>Unable to connect to the server. Ensure backend is running.</span>
        </div>
      </AdminSideBar>
    );
  }

  const bottomMetrics: MiniMetric[] = [
    {
      title: 'Predictions completed',
      value: systemMetrics.predictions_completed.toString(),
      subtext: 'Last 24 hours',
      icon: <MicrochipIcon className="w-5 h-5" />,
    },
    {
      title: 'Model health',
      value: systemMetrics.model_health,
      subtext: 'Operational',
      statusText: systemMetrics.model_health === 'Operational' ? 'Operational' : 'Degraded',
      icon: <HeartIcon className="w-5 h-5" />,
    },
    {
      title: 'Avg. prediction confidence',
      value: `${systemMetrics.avg_confidence_percent}%`,
      subtext: 'High confidence',
      statusText: systemMetrics.avg_confidence_percent > 80 ? 'High confidence' : 'Review needed',
      icon: <LineChartIcon className="w-5 h-5" />,
    },
    {
      title: 'Data source sync',
      value: 'Connected',
      subtext: systemMetrics.last_sync_time,
      icon: <DownloadCloudIcon className="w-5 h-5" />,
    },
  ];

  return (
    <AdminSideBar hideLoginRegister>
      <div className="w-full space-y-6">
        <NotificationToastHost />
        <PageHeader
          title="FireAway System Dashboard"
          subtitle="Overview of active fires, predictions, and system health"
          showIcons
        />

        <DashboardMetrics metrics={topMetrics} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 w-full p-2">
          <section className="bg-base-200 border border-base-300 rounded shadow-sm p-6 flex flex-col justify-between">
            <div className="w-full">
              <h2 className="text-medium font-bold uppercase tracking-wider text-text-muted mb-4 font-display">
                Recent Activity
              </h2>
              <div className="divide-y divide-base-300 border-b border-base-300">
                {activityLog.length === 0 ? (
                  <div className="py-4 text-center text-medium text-text-muted">
                    No recemt activity
                  </div>
                ) : (
                  activityLog.map((log) => (
                    <div
                      key={log.id}
                      className="py-3 px-2 flex justify-between items-start space-x-4 my-0.5 hover:bg-base-300 transition-colors"
                    >
                      <span className="text-medium text-base-content leading-snug">
                        {log.message}
                      </span>
                      <span className="text-medium font-mono text-base-content/60 whitespace-nowrap pt-0.5">
                        {log.timeAgo}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>

          <section className="bg-base-200 border border-base-300 rounded shadow-sm p-6 flex flex-col justify-between min-h-[300px] ">
            <div className="w-full">
              <h2 className="text-medium font-bold uppercase tracking-wider text-base-content/70 mb-6 font-display">
                Incidents this week
              </h2>

              <div className="flex justify-between items-end h-48 pt-4 px-4 bg-base-300/30 rounded border border-base-300">
                {weeklyIncidents.map((day) => {
                  const percentageHeight = (day.count / maxCount) * 100;
                  return (
                    <div
                      key={day.day}
                      className="flex flex-col items-center flex-1 group mx-1.5 h-full justify-end"
                    >
                      <div className="text-[10px] font-mono text-primary mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {day.count}
                      </div>
                      <div
                        className="w-full bg-primary/80 rounded-t-sm border-t border-x border-primary group-hover:bg-primary transition-colors"
                        style={{ height: `${percentageHeight}%`, minHeight: '4px' }}
                      />
                      <span className="text-medium font-medium text-text-muted mt-2 block font-mono">
                        {day.day}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-base-300 text-[15px] text-text-muted font-mono flex justify-between">
              <span>Y-Axis Max: {maxCount} Alerts</span>
              <span> Spatial Log Distribution Context</span>
            </div>
          </section>
        </div>

        {/* <SystemMetrics metrics={bottomMetrics} /> */}
      </div>
    </AdminSideBar>
  );
};

export default AdminDashBoardDetailed;

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import Card from '../../components/ui/Card';
import { AdminSideBar } from '../../components/admin/AdminSideBar';
import { useAdminAnalytics } from '../../hooks/useAdminAnalytics';
import { PageHeader } from '../../components/layout/pageHeader';

const dateTimeFormatter = new Intl.DateTimeFormat('en-ZA', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'Africa/Johannesburg',
});

export default function AdminAnalyticsPage() {
  const { kpis, pendingRequests, loading, error, refetch } = useAdminAnalytics();
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);

  useEffect(() => {
    setUpdatedAt(dateTimeFormatter.format(new Date()));
  }, []);

  if (loading) {
    return (
      <AdminSideBar>
        <div className="p-6 flex justify-center items-center min-h-[60vh]">
          <div className="loading loading-spinner loading-lg text-primary">
            Loading analytics data...
          </div>
        </div>
      </AdminSideBar>
    );
  }

  if (error) {
    return (
      <AdminSideBar>
        <div className="p-6">
          <div className="bg-error/10 border border-error/30 rounded-lg p-4 text-error">
            <p className="font-semibold">Unable to load analytics</p>
            <p className="text-sm">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        </div>
      </AdminSideBar>
    );
  }

  if (!kpis) {
    return (
      <AdminSideBar>
        <div className="p-6">No data available</div>
      </AdminSideBar>
    );
  }

  const kpiCards = [
    { label: 'Total Users', value: kpis.total_users.toString() },
    { label: 'Pending Role Requests', value: kpis.pending_role_requests.toString() },
    { label: 'Total Firefighters', value: kpis.total_firefighters.toString() },
    { label: 'Total Admins', value: kpis.total_admins.toString() },
  ];

  return (
    <AdminSideBar>
      <div className="p-6 space-y-6 w-full">
        {/* Header */}
        <PageHeader
          title="Admin Analytics"
          subtitle="User governance and role management overview"
          showIcons
          actions={
            <span className="text-sm text-text-primary/40">
              Updated: {new Date().toLocaleString()}
            </span>
          }
        />

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiCards.map((kpi) => (
            <Card key={kpi.label} title={kpi.label}>
              <div className="flex flex-col">
                <span className="text-2xl font-bold text-text-primary">{kpi.value}</span>
                {/* No change indicator for now */}
              </div>
            </Card>
          ))}
        </div>

        {/* Pending Role Requests */}
        <Card
          title="Pending Role Requests"
          actions={
            <Link href="/admin/approvals" className="text-sm text-primary hover:underline">
              Manage all
            </Link>
          }
        >
          {pendingRequests.length === 0 ? (
            <p className="text-white/40 text-sm">No pending requests</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-carbon-stroke">
                    <th className="text-left py-2 text-white/40 font-medium">Name</th>
                    <th className="text-left py-2 text-white/40 font-medium">Email</th>
                    <th className="text-left py-2 text-white/40 font-medium">Requested Role</th>
                    <th className="text-left py-2 text-white/40 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingRequests.map((req) => (
                    <tr
                      key={req.request_id}
                      className="border-b border-carbon-stroke/50 last:border-0"
                    >
                      <td className="py-2 text-text-primary">
                        {req.user.name} {req.user.surname}
                      </td>
                      <td className="py-2 text-white/80">{req.user.email}</td>
                      <td className="py-2">
                        <span className="badge badge-neutral">{req.requested_role}</span>
                      </td>
                      <td className="py-2 text-white/60">
                        {dateTimeFormatter.format(new Date(req.created_at))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </AdminSideBar>
  );
}

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import { AdminSideBar } from '../../components/admin/adminSidebar';
interface KPIs {
  total_users: number;
  pending_role_requests: number;
  total_firefighters: number;
  total_admins: number;
}

interface UserSummary {
  id: string;
  name: string;
  surname: string;
  email: string;
  license_number: string | null;
}

interface PendingRequest {
  request_id: string;
  user: UserSummary;
  requested_role: string;
  current_role: string;
  status: string;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
}

interface AnalyticsData {
  kpis: KPIs;
  pending_requests: PendingRequest[];
}

export default function AdminAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/admin/analytics/overview')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status}`);
        }
        return res.json();
      })
      .then((data: AnalyticsData) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching analytics:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <AdminSideBar>
        <div className="p-6 flex justify-center items-center min-h-[60vh]">
          <div className="loading loading-spinner loading-lg text-primary">Loading analytics data...</div>
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

  if (!data) {
    return (
      <AdminSideBar>
        <div className="p-6">No data available</div>
      </AdminSideBar>
    );
  }

  const kpiCards = [
    { label: 'Total Users', value: data.kpis.total_users.toString() },
    { label: 'Pending Role Requests', value: data.kpis.pending_role_requests.toString() },
    { label: 'Total Firefighters', value: data.kpis.total_firefighters.toString() },
    { label: 'Total Admins', value: data.kpis.total_admins.toString() },
  ];

  return (
    <AdminSideBar>
      <div className="p-6 space-y-6 w-full">

        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
              Admin Analytics
            </h1>
            <p className="text-sm text-neutral/50">
              User governance and role management overview
            </p>
          </div>
          <span className="text-sm text-neutral/40">
            Updated: {new Date().toLocaleString()}
          </span>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiCards.map((kpi) => (
            <Card key={kpi.label} title={kpi.label}>
              <div className="flex flex-col">
                <span className="text-2xl font-bold text-neutral">{kpi.value}</span>
                {/* No change indicator for now */}
              </div>
            </Card>
          ))}
        </div>

        {/* Pending Role Requests */}
        <Card
          title="Pending Role Requests"
          actions={
            <Link href="/admin/approvalPage" className="text-sm text-primary hover:underline">
              Manage all
            </Link>
          }
        >
          {data.pending_requests.length === 0 ? (
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
                  {data.pending_requests.map((req) => (
                    <tr key={req.request_id} className="border-b border-carbon-stroke/50 last:border-0">
                      <td className="py-2 text-neutral">
                        {req.user.name} {req.user.surname}
                      </td>
                      <td className="py-2 text-white/80">{req.user.email}</td>
                      <td className="py-2">
                        <Badge label={req.requested_role} state="pending" />
                      </td>
                      <td className="py-2 text-white/60">
                        {new Date(req.created_at).toLocaleString()}
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
import React from 'react';
import Link from 'next/link';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import Button from '../../components/Button';
import { SideBarLayout } from '../../components/demoSidebar';

// --------------------- DUMMY DATA ---------------------
const kpiData = [
  { label: 'Total Users', value: '1,284', change: '+12%', trend: 'up' },
  { label: 'Pending Role Requests', value: '23', change: '-3%', trend: 'down' },
  { label: 'Role Changes (30d)', value: '47', change: '+5%', trend: 'up' },
  { label: 'Suspended / Revoked', value: '12', change: '-2%', trend: 'down' },
];

const pendingRequests = [
  { email: 'jane.doe@example.com', requestedRole: 'Firefighter', timestamp: '2 hours ago' },
  { email: 'mike.smith@example.com', requestedRole: 'Admin', timestamp: '1 day ago' },
  { email: 'sara.connor@example.com', requestedRole: 'Firefighter', timestamp: '3 days ago' },
];

const recentAuditLog = [
  { timestamp: '10:32 AM', user: 'admin@epiuse.com', action: 'Role Change', details: 'jane.doe → Firefighter' },
  { timestamp: '09:15 AM', user: 'fire.chief@epiuse.com', action: 'Login', details: 'Success' },
  { timestamp: '08:45 AM', user: 'admin@epiuse.com', action: 'Revocation', details: 'sara.connor (suspended)' },
  { timestamp: '07:20 AM', user: 'system', action: 'Password Reset', details: 'mike.smith' },
  { timestamp: 'Yesterday, 23:10', user: 'admin@epiuse.com', action: 'Role Approval', details: 'alice.wong → Admin' },
];

export default function AdminAnalyticsPage() {
  return (
    <SideBarLayout>
      <div className="p-6 space-y-6 w-full">

        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
              Admin Analytics
            </h1>
            <p className="text-sm text-neutral/50">
              Governance, security, and system performance insights
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="dark" className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export Audit Log
            </Button>
            <span className="text-sm text-neutral/40">Last 30 days</span>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiData.map((kpi) => (
            <Card key={kpi.label} title={kpi.label}>
              <div className="flex flex-col">
                <span className="text-2xl font-bold text-neutral">{kpi.value}</span>
                <span className={`text-xs ${kpi.trend === 'up' ? 'text-success' : 'text-error'}`}>
                  {kpi.change}
                </span>
              </div>
            </Card>
          ))}
        </div>

        {/* Pending Role Requests */}
        <Card
          title="Pending Role Requests"
          actions={
            <Link href="/admin/role-requests" className="text-sm text-primary hover:underline">
              Manage all
            </Link>
          }
        >
          {pendingRequests.length === 0 ? (
            <p className="text-white/40 text-sm">No pending requests</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-carbon-stroke">
                  <th className="text-left py-2 text-white/40 font-medium">Email</th>
                  <th className="text-left py-2 text-white/40 font-medium">Requested Role</th>
                  <th className="text-left py-2 text-white/40 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {pendingRequests.map((req, idx) => (
                  <tr key={idx} className="border-b border-carbon-stroke/50 last:border-0">
                    <td className="py-2 text-neutral">{req.email}</td>
                    <td className="py-2">
                      <Badge label={req.requestedRole} state="pending" />
                    </td>
                    <td className="py-2 text-white/60">{req.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>

        {/* Recent Audit Log */}
        <Card
          title="Recent Audit Log"
          actions={
            <Link href="/admin/audit-log" className="text-sm text-primary hover:underline">
              View full log
            </Link>
          }
        >
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-carbon-stroke">
                <th className="text-left py-2 text-white/40 font-medium">Timestamp</th>
                <th className="text-left py-2 text-white/40 font-medium">User</th>
                <th className="text-left py-2 text-white/40 font-medium">Action</th>
                <th className="text-left py-2 text-white/40 font-medium">Details</th>
              </tr>
            </thead>
            <tbody>
              {recentAuditLog.map((entry, idx) => (
                <tr key={idx} className="border-b border-carbon-stroke/50 last:border-0">
                  <td className="py-2 text-white/60">{entry.timestamp}</td>
                  <td className="py-2 text-neutral">{entry.user}</td>
                  <td className="py-2">
                    <Badge
                      label={entry.action}
                      state="pending"
                    />
                  </td>
                  <td className="py-2 text-white/60">{entry.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

      </div>
    </SideBarLayout>
  );
}
import React from 'react';
import Link from 'next/link';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import Button from '../../components/Button';
import { SideBarLayout } from '../../components/demoSidebar';

const metrics = [
  { label: 'Total Reports', value: '1,284', change: '+12%', trend: 'up' },
  { label: 'Verified Fires', value: '347', change: '+5%', trend: 'up' },
  { label: 'Active Incidents', value: '18', change: '-2%', trend: 'down' },
  { label: 'Firefighters on Duty', value: '42', change: '+8%', trend: 'up' },
];

const recentReports = [
  { id: 'FR-2026-019', location: 'Faerie Glen', status: 'verified', time: '10 min ago' },
  { id: 'FR-2026-018', location: 'Groenkloof', status: 'pending', time: '45 min ago' },
  { id: 'FR-2026-017', location: 'Rietvlei', status: 'rejected', time: '2 hours ago' },
];

const weeklyData = [
  { day: 'Mon', count: 12 },
  { day: 'Tue', count: 8 },
  { day: 'Wed', count: 15 },
  { day: 'Thu', count: 10 },
  { day: 'Fri', count: 22 },
  { day: 'Sat', count: 18 },
  { day: 'Sun', count: 9 },
];

const maxCount = Math.max(...weeklyData.map(d => d.count));

export default function AnalyticsPage() {
  return (
    <SideBarLayout>
      <div className="p-6 space-y-6 w-full">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
              Analytics Dashboard
            </h1>
            <p className="text-sm text-neutral/50">Overview of fire incidents and system performance</p>
          </div>
          <Button variant="dark" className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export Report
          </Button>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric, idx) => (
            <Card key={metric.label} title={metric.label}>
              <div className="flex flex-col">
                <span className="text-2xl font-bold text-neutral">{metric.value}</span>
                <span className={`text-xs ${metric.trend === 'up' ? 'text-success' : 'text-error'}`}>
                  {metric.change}
                </span>
              </div>
            </Card>
          ))}
        </div>

        {/* Weekly Incidents & Recent Reports */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Weekly Incidents */}
          <Card title="Weekly Incidents">
            <div className="space-y-3">
              {weeklyData.map((item) => (
                <div key={item.day} className="flex items-center gap-2">
                  <span className="w-8 text-sm text-white/60">{item.day}</span>
                  <div className="flex-1 bg-carbon-stroke rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-ignite rounded-full"
                      style={{ width: `${(item.count / maxCount) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-white/60 w-6 text-right">{item.count}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Recent Reports */}
          <Card
            title="Recent Reports"
            actions={
              <Link href="/reports" className="text-sm text-primary hover:underline">
                View all
              </Link>
            }
          >
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-carbon-stroke">
                  <th className="text-left py-2 text-white/40 font-medium">Reference</th>
                  <th className="text-left py-2 text-white/40 font-medium">Location</th>
                  <th className="text-left py-2 text-white/40 font-medium">Status</th>
                  <th className="text-left py-2 text-white/40 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {recentReports.map((report) => (
                  <tr key={report.id} className="border-b border-carbon-stroke/50 last:border-0">
                    <td className="py-2 text-neutral">{report.id}</td>
                    <td className="py-2 text-white/80">{report.location}</td>
                    <td className="py-2">
                      <Badge label={report.status} state={report.status as any} />
                    </td>
                    <td className="py-2 text-white/60">{report.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </SideBarLayout>
  );
}
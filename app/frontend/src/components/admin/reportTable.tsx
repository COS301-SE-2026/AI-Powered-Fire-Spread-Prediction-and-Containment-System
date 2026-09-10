import React from 'react';
import { useRouter } from 'next/router';
import { FireReportMapResponse, ReportStatus } from '../../types/Report';
import { StatusBadge } from './reportStatusBadge';
import { FormatDate } from '../../lib/FormatDate';
import { VerificationNotes } from '../../lib/VerificationNotes';

interface FireReportsTableProps {
  readonly reports: FireReportMapResponse[];
  readonly filter: 'All' | ReportStatus;
}

export function FireReportsTable({ reports, filter }: FireReportsTableProps) {
  const filtered = reports
    .filter((r) => filter === 'All' || r.status === filter)
    .sort((a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime());

  const router = useRouter();

  return (
    <div className="w-full overflow-x-auto rounded-2xl border border-carbon-stroke">
      <table className="table table-pin-rows w-full">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40">
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Ref
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Location
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Status
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Reason
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Size
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Reported
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              Reporter
            </th>
            <th className="text-left text-sm font-bold font-display tracking-widest text-text-primary uppercase px-4 py-3">
              View
            </th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? (
            <tr>
              <td colSpan={8} className="px-4 py-8 text-center text-sm font-bold text-error">
                No requests found
              </td>
            </tr>
          ) : (
            filtered.map((report) => (
              <tr
                key={report.id}
                className="[&>td]:border-t [&>td]:border-carbon-card hover:bg-surface-hover even:bg-carbon-bg/80"
              >
                <td className="px-4 text-sm text-text-primary">{report.reference_number}</td>
                <td className="px-4 text-sm text-text-primary">{report.location_text}</td>
                <td className="px-4 text-sm text-text-primary">
                  <StatusBadge status={report.status} />
                </td>
                <td className="px-4 text-sm text-text-primary">
                  {VerificationNotes(report.verification_notes)}
                </td>
                <td className="px-4 text-sm text-text-primary">{report.size} ha</td>
                <td className="px-4 text-sm text-text-primary">
                  {FormatDate(report.submitted_at)}
                </td>
                <td className="px-4 text-sm text-text-primary">{report.reporter_name}</td>
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => router.push(`/admin/${report.reference_number}`)}
                    className="text-xs font-semibold btn btn-sm btn-outline border rounded-xl text-text-primary hover:bg-smoke-hover hover:text-text-primary transition-colors"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

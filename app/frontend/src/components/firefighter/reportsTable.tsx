import React from 'react';
import { useRouter } from 'next/router';
import { ReportStatus } from '../../types/Report';
import { StatusBadge } from '../admin/reportStatusBadge';
import { FirefighterReportTable } from '../../types/FirefighterReports';
import { FormatDate } from '../../lib/FormatDate';
import { VerificationNotes } from '../../lib/VerificationNotes';

interface ReportsTableProp {
  readonly requests: FirefighterReportTable[];
  readonly filter: 'all' | ReportStatus;
  readonly onView: (request: FirefighterReportTable) => void;
}

export function ReportsTable({ requests, filter, onView }: ReportsTableProp) {
  const filtered = requests.filter((req) => filter === 'all' || req.status === filter);
  const router = useRouter();
  return (
    <div className="overflow-x-auto rounded-2xl border border-carbon-stroke max-h-150 w-full">
      <table className="table table-pin-rows">
        <thead>
          <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40 ">
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Ref
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Location
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Status
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Reason
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Size
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Reported
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase">
              Reporter
            </th>
            <th className="text-left text-xs font-bold tracking-widest text-text-primary uppercase" />
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 ? ( // no reports with any filyter which means table is empty
            <tr>
              <td colSpan={6} className="px-4 py-8 text-center text-sm font-bold text-error">
                No reports in the table
              </td>
            </tr>
          ) : (
            filtered.map((req) => (
              <tr key={req.ref} className="hover:bg-(--color-surface-hover) even:bg-carbon-bg/80">
                <td className="py-4 text-sm text-text-primary border-t border-carbon-card">
                  {req.ref}
                </td>
                <td className="py-4 text-sm text-text-primary border-t border-carbon-card">
                  {req.location}
                </td>
                <td className="py-4 text-sm text-text-primary border-t border-carbon-card">
                  <StatusBadge status={req.status} />
                </td>
                <td className="px-4 text-sm text-text-primary">
                  {VerificationNotes(req.verification_notes)}
                </td>
                <td className="py-4 text-sm text-text-primary border-t border-carbon-card">
                  {req.size} ha
                </td>
                <td className="px-4 text-sm text-text-primary">{FormatDate(req.reported)}</td>
                <td className="py-4 text-sm text-text-primary border-t border-carbon-card">
                  {req.reporter}
                </td>
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => router.push(`/firefighter/${req.ref}`)}
                    className="text-xs font-semibold btn btn-sm btn-outline text-text-primary rounded-lg border hover:bg-smoke-hover hover:text-text-primary transition-colors"
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

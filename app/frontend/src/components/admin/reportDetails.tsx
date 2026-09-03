import React from 'react';
import { Card } from './Card';
import type { FireReportDetailResponse } from '../../types/Report';
import { StatusBadge } from './reportStatusBadge';

interface ReportDetailsProps {
  readonly report: FireReportDetailResponse;
}

export function ReportDetails({ report }: ReportDetailsProps) {
  return (
    <Card title="Report Details">
      <div className="flex flex-col gap-3">
        <div className="flex justify-between">
          <span className="text-text-muted text-sm">Reference</span>
          <code>{report.reference_number}</code>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-text-muted text-sm">Status</span>
          <StatusBadge status={report.status} />
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted text-sm">Reporter</span>
          <span className="text-text-primary">{report.reporter_name}</span>
        </div>
        <div className="flex flex-col gap-1">
          <span className='text-text-primary'>
            <span className="text-text-muted text-sm mr-1">Location</span>{report.location_text}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted text-sm">Size</span>
          <span className="text-text-primary">{report.size} ha</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-muted text-sm">Reported at</span>
          <time>
            {new Date(report.submitted_at).toLocaleDateString('en-ZA', {
              day: 'numeric',
              month: 'short',
            })}
            {' | '}
            {new Date(report.submitted_at).toLocaleTimeString('en-ZA', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </time>
        </div>
      </div>
    </Card>
  );
}

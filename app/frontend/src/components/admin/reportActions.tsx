import React, { useState, useEffect } from 'react';
import { Card } from './Card';
import { useReportStatus } from '../../hooks/useReportStatus';
import type { FireReportDetailResponse, ReportStatus } from '../../types/Report';

interface ReportActionsProps {
  readonly reportRef: string;
  readonly status: ReportStatus;
  readonly onStatusChange: (report: FireReportDetailResponse) => void;
}

export function ReportActions({ reportRef, status, onStatusChange }: ReportActionsProps) {
  const { updateStatus, loading, error } = useReportStatus();
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!success) return;
    const timer = setTimeout(() => setSuccess(null), 3000);
    return () => clearTimeout(timer);
  }, [success]);

  const handleChange = async (newStatus: ReportStatus) => {
    const updated = await updateStatus(reportRef, newStatus);
    if (updated) {
      onStatusChange(updated);
      setSuccess(`Report successfully updated to ${newStatus}.`);
    }
  };

  const handleVerify = () => handleChange('verified');
  const handleReject = () => handleChange('rejected');
  const handleRevoke = () => handleChange('pending');
  const handleReVerify = () => handleChange('pending');

  return (
    <Card title="Action">
      {success && (
        <div
          role="alert"
          className="alert bg-status-success/10 border border-status-success/30 text-status-success text-medium mb-2"
        >
          <span>{success}</span>
        </div>
      )}
      {error && (
        <div
          role="alert"
          className="alert bg-status-error/10 border border-status-error/30 text-status-error text-medium mb-2"
        >
          <span>{error}</span>
        </div>
      )}

      {status === 'verified' && (
        <div className="flex flex-col gap-3">
          <p className="text-text-muted text-sm">
            This report has already been verified. Revoke if report is falsely verified.
          </p>
          <button
            type="button"
            className="btn btn-error btn-sm text-lg"
            onClick={handleRevoke}
            disabled={loading}
          >
            {loading ? 'Updating...' : 'Revoke'}
          </button>
        </div>
      )}

      {status === 'rejected' && (
        <div className="flex flex-col gap-3">
          <p className="text-text-muted text-medium">
            This report was rejected. Send to be re-verified.
          </p>
          <button
            type="button"
            className="btn btn-primary btn-medium text-lg"
            onClick={handleReVerify}
            disabled={loading}
          >
            {loading ? 'Updating...' : 'Re-verify'}
          </button>
        </div>
      )}

      {(status === 'pending' || status === 'received') && (
        <div className="flex flex-col gap-3">
          <p className="text-text-muted text-medium">
            Review the fire report. Reject or verify manually.
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              className="btn btn-primary btn-sm flex-1 text-lg"
              onClick={handleVerify}
              disabled={loading}
            >
              {loading ? 'Updating...' : 'Verify'}
            </button>
            <button
              type="button"
              className="btn btn-error btn-sm flex-1 text-lg"
              onClick={handleReject}
              disabled={loading}
            >
              {loading ? 'Updating...' : 'Reject'}
            </button>
          </div>
        </div>
      )}
    </Card>
  );
}

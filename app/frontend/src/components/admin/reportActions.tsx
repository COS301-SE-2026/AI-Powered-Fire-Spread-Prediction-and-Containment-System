import React, { useState } from "react";
import { Card } from "./Card";
import type { FireReport, ReportStatus } from "../../types/report";

interface ReportActionsProps {
    readonly report_ref: string;
    readonly status: ReportStatus;
    readonly onStatusChange: (report: FireReport) => void;
}

export function ReportActions({ report_ref, status, onStatusChange }: ReportActionsProps) {
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function statusChange(newStatus: ReportStatus) {
        setLoading(true);
        setError(null);
        setSuccess(null);
        try{
            const res = await fetch(`/api/admin/reported-fires/${report_ref}/status?status=${newStatus}`, {
                method: 'PATCH',
            });
            if (!res.ok) throw new Error("Failed to update status");
            const updated: FireReport = await res.json();
            onStatusChange(updated);
            setSuccess(`Report successfully updated to ${newStatus}.`);
            setTimeout(() => setSuccess(null), 3000);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    const handleVerify = () => statusChange('verified');
    const handleReject = () => statusChange('rejected');
    const handleRevoke = () => statusChange('pending');
    const handleReVerify = () => statusChange('pending');

    return (
        <Card title="Action">
            {success && (
                <div role="alert" className="alert bg-status-success/10 border border-status-success/30 text-status-success text-sm mb-2">
                    <span>{success}</span>
                </div>
            )}
            {error && (
                <div role="alert" className="alert bg-status-error/10 border border-status-error/30 text-status-error text-sm mb-2">
                    <span>{error}</span>
                </div>
            )}

            {status === "verified" && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">This report has already been verified. Revoke if report is falsely verified.</p>
                    <button type="button" className="btn btn-error btn-sm" onClick={handleRevoke} disabled={loading}>{loading ? 'Updating...' : 'Revoke'}</button>
                </div>
            )}

            {status === "rejected" && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">This report was rejected. Send to be re-verified.</p>
                    <button type="button" className="btn btn-primary btn-sm" onClick={handleReVerify} disabled={loading}>{loading ? 'Updating...' : 'Re-verify'}</button>
                </div>
            )}

            {(status === "pending" || status === "received") && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">Review the fire report. Reject or verify manually.</p>
                    <div className="flex gap-2">
                        <button type="button" className="btn btn-primary btn-sm flex-1" onClick={handleVerify} disabled={loading}>{loading ? 'Updating...' : 'Verify'}</button>
                        <button type="button" className="btn btn-error btn-sm flex-1" onClick={handleReject} disabled={loading}>{loading ? 'Updating...' : 'Reject'}</button>
                    </div>
                </div>
            )}
        </Card>
    );
}
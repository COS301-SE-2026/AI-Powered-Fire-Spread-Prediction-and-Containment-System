import React, { useState } from "react";
import { Card } from "./Card";
import type { ReportModal, ReportStatus } from "../../types/firefighter";
import Button from "../Button";

interface ReportActionsProps {
    readonly report_id: string;
    readonly status: ReportStatus;
    readonly onStatusChange: (report: ReportModal) => void;
}

export function ReportActions({ report_id, status, onStatusChange }: ReportActionsProps) {
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function statusChange(newStatus: ReportStatus) {
        setLoading(true);
        setError(null);
        setSuccess(null);
        try{
            const res = await fetch(`/api/admin/reported-fires/${report_id}/status?status=${newStatus}`, {
                method: 'PATCH',
            });
            if (!res.ok) throw new Error("Failed to update status");
            const updated: ReportModal = await res.json();
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
                    <Button variant="red" onClick={handleRevoke} disabled={loading}>{loading ? 'Updating...' : 'Revoke'}</Button>
                </div>           
            )}
            
            {status === "rejected" && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">This report was rejected. Send to be re-verified.</p>
                    <Button variant="fire" onClick={handleReVerify} disabled={loading}>{loading ? 'Updating...' : 'Re-verify'}</Button>
                </div>
            )}

            {(status === "pending" || status === "received") && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">Review the fire report. Reject or verify manually.</p>
                    <div className="flex gap-2">
                        <Button variant="fire" className="flex-1" onClick={handleVerify} disabled={loading}>{loading ? 'Updating...' : 'Verify'}</Button>
                        <Button variant="red" className="flex-1" onClick={handleReject} disabled={loading}>{loading ? 'Updating...' : 'Reject'}</Button>
                    </div>
                </div>
            )}
        </Card>
    );
}
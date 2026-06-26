import React, { useState } from "react";
import { Card } from "./Card";
import type { ReportStatus } from "../../types/report";
import Button from "../Button";

interface ReportActionsProps {
    readonly report_id: string;
    readonly status: ReportStatus;
}

export function ReportActions({ report_id, status }: ReportActionsProps) {
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleVerify = () => {
        //api call
        setSuccess('Report successfully verified.');
        setError(null);
        setTimeout(() => setSuccess(null), 3000);
    };

    const handleReject = () => {
        //api call
        setSuccess('Report successfully rejected.');
        setError(null);
        setTimeout(() => setSuccess(null), 3000);
    };

    const handleRevoke = () => {
        //api call
        setSuccess('Verification revoked successfully.');
        setError(null);
        setTimeout(() => setSuccess(null), 3000);
    };

    const handleReVerify = () => {
        //api call
        setSuccess('Report sent for re-verification.');
        setError(null);
        setTimeout(() => setSuccess(null), 3000);
    }

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
                    <Button variant="red" onClick={handleRevoke}>Revoke</Button>
                </div>           
            )}
            
            {status === "rejected" && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">This report was rejected. Send to be re-verified.</p>
                    <Button variant="fire" onClick={handleReVerify}>Re-verify</Button>
                </div>
            )}

            {status === "pending" && (
                <div className="flex flex-col gap-3">
                    <p className="text-text-muted text-sm">Review the fire report. Reject or verify manually.</p>
                    <div className="flex gap-2">
                        <Button variant="fire" className="flex-1" onClick={handleVerify}>Verify</Button>
                        <Button variant="red" className="flex-1" onClick={handleReject}>Reject</Button>
                    </div>
                </div>
            )}
        </Card>
    );
}
import React from "react";
import { Card } from "./Card";
import type { FireReport } from "../../types/report";
import { StatusBadge } from "./reportStatusBadge";

interface ReportDetailsProps {
    readonly report: FireReport;
}

export function ReportDetails({ report }: ReportDetailsProps) {
    return (
        <Card title="Report Details">
            <div className="flex flex-col gap-3">
                <div className="flex justify-between">
                    <span className="text-text-muted text-sm">Reference</span>
                    <code>{report.report_id}</code>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-text-muted text-sm">Status</span>
                    <StatusBadge status={report.status} />
                </div>
                <div className="flex justify-between">
                    <span className="text-text-muted text-sm">Reporter</span>
                    <span className="text-text-primary">{report.reporter}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-text-muted text-sm">Location</span>
                    <span className="text-text-primary">{report.location}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-text-muted text-sm">Size</span>
                    <span className="text-text-primary">{report.size}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-text-muted text-sm">Reported at</span>
                    <time>
                        {report.reported_at.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short'})}
                        {' | '}
                        {report.reported_at.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit'})}
                    </time>
                </div>
            </div>
        </Card>
    );
}
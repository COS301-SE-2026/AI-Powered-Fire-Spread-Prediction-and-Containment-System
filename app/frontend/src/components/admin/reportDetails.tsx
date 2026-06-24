import React from "react";
import { Card } from "./Card";
import type { FireReport } from "../../types/report";

interface ReportDetailsProps {
    readonly report: FireReport;
}

export function ReportDetails({ report }: ReportDetailsProps) {
    return (
        <Card title="Report Details">
            <div className="flex flex-col gap-3">
                <div className="flex justify-between">
                    <label>Reference</label>
                    <code>{report.report_id}</code>
                </div>
                <div className="flex justify-between">
                    <label>Reporter</label>
                    <span className="text-text-primary">{report.reporter}</span>
                </div>
                <div className="flex justify-between">
                    <label>Location</label>
                    <span className="text-text-primary">{report.location}</span>
                </div>
                <div className="flex justify-between">
                    <label>Size</label>
                    <span className="text-text-primary">{report.size}</span>
                </div>
                <div className="flex justify-between">
                    <label>Reported at</label>
                    <time>
                        {report.reported_at.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short'})}
                        {' - '}
                        {report.reported_at.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit'})}
                    </time>
                </div>
            </div>
        </Card>
    );
}
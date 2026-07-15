import React from "react";
import { Card } from "./Card";
import type { FireReport } from "../../types/report";

interface ReportPhotoProps {
    readonly report: FireReport;
}

export function ReportPhoto({ report }: ReportPhotoProps) {
    return (
        <Card title="Photo Evidence">
            {report.image_url ? (
                <img src={report.image_url} alt="Fire report evidence" className="w-full rounded-lg object-cover h-48 bg-carbon-card"/>
            ) : (
                <div className="flex flex-col items-center justify-center h-48 rounded-lg border border-dashed border-carbon-stroke gap-2">
                    <span className="text-text-muted text-sm">No photo attached</span>
                </div>
            )}
        </Card>
    );
}
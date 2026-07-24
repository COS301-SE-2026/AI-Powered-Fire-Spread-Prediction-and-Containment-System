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
                <img src={report.image_url} alt="Fire report evidence" className="w-full  max-h-96 rounded-lg object-contain bg-carbon-card"/>
            ) : (
                <div className="flex flex-col items-center justify-center h-48 rounded-lg border border-carbon-stroke gap-2">
                    <span className="text-text-muted text-sm">No photo attached</span>
                </div>
            )}
        </Card>
    );
}
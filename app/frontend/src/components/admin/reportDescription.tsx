import React from "react";
import { Card } from "./Card";
import type { FireReport } from "../../types/Report";

interface ReportDescriptionProps {
    readonly report: FireReport;
}

export function ReportDescription({ report }: ReportDescriptionProps) {
    return (
        <Card title="Description">
            {report.description ? (
                <p className="text-text-primary">{report.description}</p>
            ) : (
                <p className="text-text-muted italic">No description provided.</p>
            )}
        </Card>
    );
}
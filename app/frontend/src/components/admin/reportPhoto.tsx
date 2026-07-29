import React from "react";
import { Card } from "./Card";
import type { FireReport } from "../../types/report";
import Image from "next/image";

interface ReportPhotoProps {
    readonly report: FireReport;
}

export function ReportPhoto({ report }: ReportPhotoProps) {
    return (
        <Card title="Photo Evidence">
            {report.image_url ? (
                <div className="relative w-full h-96 rounded-lg overflow-hidden bg-carbon-card">
                    <Image src={report.image_url} alt="Fire report evidence" fill unoptimized sizes="(max-width: 1280px) 100vw, 33vw" className="object-contain"/>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center h-48 rounded-lg border border-carbon-stroke gap-2">
                    <span className="text-text-muted text-sm">No photo attached</span>
                </div>
            )}
        </Card>
    );
}
import React, { useState } from "react";
import { Card } from "./Card";
import type { FireReport } from "../../types/Report";
import Image from "next/image";

interface ReportPhotoProps {
    readonly report: FireReport;
}

export function ReportPhoto({ report }: ReportPhotoProps) {
    const [hasError, setHasError] = useState(false);
    const showImage = report.image_url && !hasError;
    return (
        <Card title="Photo Evidence">
            {showImage? (
                <div className="relative w-full h-96 rounded-lg overflow-hidden bg-carbon-card">
                    <Image src={report.image_url} alt="Fire report evidence" fill unoptimized sizes="(max-width: 1280px) 100vw, 33vw" className="object-contain" onError={() => setHasError(true)}/>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center h-48 rounded-lg border border-carbon-stroke gap-2">
                    <span className="text-error text-sm font-medium">No photo evidence found</span>
                </div>
            )}
        </Card>
    );
}
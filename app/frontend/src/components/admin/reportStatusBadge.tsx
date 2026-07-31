import React from "react";
import { statusBadge } from "./statusBadge";
import type { ReportStatus } from "../../types/report";

interface StatusBadgeProps {
    readonly status: ReportStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
    const displayStatus = status === 'received' ? 'pending' : status;
    const { bg = 'bg-carbon-card', text = 'text-text-primary/50', border = '' } = statusBadge[displayStatus] ?? {};

    return (
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${bg} ${text} ${border}`}>
            {displayStatus}
        </span>
    );
}
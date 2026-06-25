import React from "react";
import { statusBadge, BadgeStyle } from "./statusBadge";
import type { ReportStatus } from "../../types/report";

interface StatusBadgeProps {
    readonly status: ReportStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
    const { bg = 'bg-carbon-card', text = 'text-neutral/50', border = '' } = statusBadge[status] ?? {};

    return (
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${bg} ${text} ${border}`}>
            {status}
        </span>
    );
}
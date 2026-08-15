import React from "react";
import { ReportStatus } from "../../types/Report";

type TableStatusFilter = 'all' | ReportStatus;

interface StatusTableFilterProps {
    readonly filter: TableStatusFilter;
    readonly onChange: (filter: TableStatusFilter) => void;
}

const filters: TableStatusFilter[] = ['all', 'pending', 'verified', 'rejected'];

export function StatusTableFilter({ filter, onChange }: StatusTableFilterProps) {
  return <div className="flex gap-2 mb-2">
            {filters.map((filt) => (
                <button type="button" key={filt} onClick={() => onChange(filt)} className={`text-xs px-4 py-1.5 font-semibold rounded-full border transition-colors uppercase ${filter === filt ? 'bg-torch/25 text-flare border-ignite/40' : 'border-carbon-card text-text-primary hover:bg-smoke-hover'}`}>
                    {filt}
                </button>
            ))}
        </div>
}
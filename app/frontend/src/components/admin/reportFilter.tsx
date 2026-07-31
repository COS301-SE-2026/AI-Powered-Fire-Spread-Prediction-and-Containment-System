import React from "react";
import { ReportStatus } from "../../types/report";

type FilterOption = 'All' | ReportStatus;

interface RoleFilterTabsProps {
    readonly filter: FilterOption;
    readonly onChange: (filter: FilterOption) => void;
}

const filters: FilterOption[] = ['All', 'pending', 'verified', 'rejected'];

export function ReportFilterTabs({ filter, onChange }: RoleFilterTabsProps) {
    return(
        <div className="flex gap-2">
            {filters.map((fil) => (
                <button type="button" key={fil} onClick={() => onChange(fil)} className={`text-xs font-semibold px-4 py-1.5 rounded-full border transition-colors capitalize ${filter === fil ? 'bg-ignite/20 text-flare border-ignite/30' : 'border-carbon-card text-text-primary/50 hover:bg-smoke-hover'}`}>
                    {fil}
                </button>
            ))}
        </div>
    );
}
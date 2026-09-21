import { RESOURCE_GROUPS } from "../../lib/ResourceGroups";

export function ResourceMapLegend() {
    return (
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 px-1 text-xs text-text-muted">
            {Object.values(RESOURCE_GROUPS).map((g) => {
                const Icon = g.icon;
                return (
                    <span key={g.label} className="flex items-center gap-1.5">
                        <span className="inline-block size-3 rounded-sm" style={{ background: g.color }}></span>
                        {g.label}
                    </span>
                );
            })}
        </div>
    );
}
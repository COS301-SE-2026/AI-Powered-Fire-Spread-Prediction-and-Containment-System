import React from 'react';
import { ChevronRight } from 'lucide-react';
import type { NearbyFire } from '../../types/FirefighterDashboard';

interface GuestReportProps {
  readonly reports: NearbyFire[];
  readonly selectedFireId?: string | null;
  readonly onSelectFire?: (ref: string) => void;
}

export function GuestReports({ reports, selectedFireId, onSelectFire }: GuestReportProps) {
  const verifiedReports = reports.filter((r) => r.status?.toLowerCase() === 'verified');

  if (!verifiedReports.length) return <div className="p-4 text-xs opacity-50">No reports</div>;

  return (
    <div className="h-full overflow-y-auto flex flex-col p-2">
      {verifiedReports.map((r) => (
        <div key={r.reference_number} onClick={() => onSelectFire?.(r.reference_number)} className={`flex items-center justify-between rounded-lg px-3 py-2.5 border border-carbon-stroke hover:border-ignite mb-2 hover:bg-carbon-card/50 cursor-pointer transition-colors ${r.reference_number === selectedFireId ? 'bg-carbon-card/70 border-ignite' : ''}`}>
            <div>
              <p className="font-semibold text-sm">{r.location_text}</p>
              <p className="text-xs opacity-50">
                {r.distance} km · {r.time_ago}
              </p>
            </div>
            <div className="flex items-center gap-1">
              <ChevronRight className="size-4 opacity-30" />
            </div>
          </div>
        ))}
      </div>
  );
}

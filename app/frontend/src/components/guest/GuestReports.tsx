import React from 'react';
import { ChevronRight } from 'lucide-react';

interface Report {
  readonly id: string;
  readonly location_text: string;
  readonly  status: string;
  readonly distance: number;
  readonly time_ago: string;
}

export function GuestReports({ reports }: { reports: Report[] }) {
  if (!reports.length) return <div className="p-4 text-xs opacity-50">No reports</div>;

  const statusColor = (s: string) => {
    const map: Record<string, string> = {
      verified: 'bg-ignite/20 text-flare border border-ignite/40',
      pending: 'bg-torch/20 text-torch border border-torch/35',
      received: 'bg-humidity/20 text-humidity border border-humidity/35',
    };
    return map[s.toLowerCase()] || 'bg-carbon-card text-neutral/50';
  };

  return (
    <div className="divide-y divide-carbon-stroke">
      {reports.map(r => (
        <div key={r.id} className="flex items-center justify-between px-3 py-2 hover:bg-carbon-card/50 cursor-pointer transition-colors">
          <div>
            <p className="font-semibold text-sm">{r.location_text}</p>
            <p className="text-xs opacity-50">{r.distance.toFixed(1)} km · {r.time_ago}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`badge px-3 py-1 rounded-full ${statusColor(r.status)}`}>{r.status}</span>
            <ChevronRight className="size-4 opacity-30" />
          </div>
        </div>
      ))}
    </div>
  );
}
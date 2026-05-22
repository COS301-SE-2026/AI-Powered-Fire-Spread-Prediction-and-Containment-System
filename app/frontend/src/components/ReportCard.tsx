import React from 'react';
import { MapPin, Clock } from 'lucide-react';

interface ReportCardProps {
  location: string;
  distance: string;
  timeAgo: string;
}

export default function ReportCard({ location, distance, timeAgo }: ReportCardProps) {
  return (
    <div className="flex items-center justify-between bg-white/3 hover:bg-white/5 border border-white/5 rounded-[var(--radius-md)] px-3 py-2.5 transition-colors cursor-pointer group">
      <div className="min-w-0">
        <p className="font-display font-bold text-[13px] uppercase tracking-wide text-white/80 group-hover:text-white transition-colors truncate">
          {location}
        </p>
        <div className="flex items-center gap-1 mt-0.5">
          <MapPin size={9} className="text-white/25 shrink-0" />
          <span className="font-mono text-[10px] text-white/30">{distance}</span>
        </div>
      </div>
      <div className="flex items-center gap-1 shrink-0 ml-2">
        <Clock size={9} className="text-white/25" />
        <span className="font-mono text-[10px] text-white/30">{timeAgo}</span>
      </div>
    </div>
  );
}
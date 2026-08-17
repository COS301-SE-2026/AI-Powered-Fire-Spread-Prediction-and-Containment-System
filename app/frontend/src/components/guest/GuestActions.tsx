import React from 'react';
import { useRouter } from 'next/router';
import { Flame, LocateFixed } from 'lucide-react';

interface GuestActionsProps {
  readonly onRecenter: () => void;
}

export function GuestActions({ onRecenter }: GuestActionsProps) {
  const router = useRouter();

  const handleReportFire = () => {
    router.push('/guests/live-map');
  };
  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={handleReportFire}
        className="w-46 px-4 py-2 text-lg font-medium rounded transition-colors bg-carbon-side/40 text-text-primary/70 hover:bg-carbon-side/60"
      >
        <Flame className="size-15" />
        Report Fire
      </button>
      <button
        type="button"
        onClick={onRecenter}
        className="w-46 px-4 py-2 text-lg font-medium rounded transition-colors bg-carbon-side/40 text-text-primary/70 hover:bg-carbon-side/60"
      >
        <LocateFixed className="size-15" />
        Recenter
      </button>
    </div>
  );
}

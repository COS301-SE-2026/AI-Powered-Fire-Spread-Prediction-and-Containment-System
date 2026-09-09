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
    <div className="grid grid-cols-2 gap-2 w-full">
      <button
        type="button"
        onClick={handleReportFire}
        className="flex flex-col items-center justify-center gap-1 w-full px-2 py-3 text-sm sm:text-base font-medium rounded-lg transition-colors bg-carbon-side/40 text-text-muted hover:bg-carbon-side/60 border border-carbon-stroke"
      >
        <Flame className="size-5 sm:size-6" />
        Report Fire
      </button>
      <button
        type="button"
        onClick={onRecenter}
        className="flex flex-col items-center justify-center gap-1 w-full px-2 py-3 text-sm sm:text-medium font-medium rounded-lg transition-colors bg-carbon-side/40 text-text-muted hover:bg-carbon-side/60 border border-carbon-stroke"
      >
        <LocateFixed className="size-5 sm:size-6" />
        Recenter
      </button>
    </div>
  );
}

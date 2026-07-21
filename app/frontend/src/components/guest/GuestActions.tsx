import React from 'react';
import { useRouter } from 'next/router';

interface GuestActionsProps {
  readonly onRecenter: () => void;
}

export function GuestActions({ onRecenter }: GuestActionsProps) {
  const router = useRouter();

  const handleReportFire = () => {
    router.push('/guests/guestsReportFire');
  };
  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={handleReportFire}
        className="px-4 py-2 text-m font-medium rounded transition-colors bg-carbon-side/40 text-neutral/70 hover:bg-carbon-side/60"
      >
        🔥 Report Fire
      </button>
      <button
        type="button"
        onClick={onRecenter}
        className="px-4 py-2 text-m font-medium rounded transition-colors bg-carbon-side/40 text-neutral/70 hover:bg-carbon-side/60"
      >
        🏡 Recenter
      </button>
    </div>
  );
}
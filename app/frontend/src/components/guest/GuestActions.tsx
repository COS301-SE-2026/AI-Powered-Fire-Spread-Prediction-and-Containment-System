import React from 'react';

interface GuestActionsProps {
  readonly isDrawMode: boolean;
  readonly onToggleDraw: () => void;
 // readonly onUndo: () => void;
  //readonly onClear: () => void;
  readonly onRecenter: () => void;
  //readonly canUndo: boolean;
  //readonly canClear: boolean;
}

export function GuestActions({
  isDrawMode,
  onToggleDraw,
  //onUndo,
  //onClear,
  onRecenter,
  //canUndo,
  //canClear,
}: GuestActionsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={onToggleDraw}
        className={`px-4 py-2 text-xs font-medium rounded transition-colors ${
          isDrawMode
            ? 'bg-ignite/20 text-ignite border border-ignite/50'
            : 'bg-carbon-side/40 text-neutral/70 hover:bg-carbon-side/60'
        }`}
      >
        {isDrawMode ? 'Cancel Draw' : 'Draw Line'}
      </button>
      {/*<button
      type='button'
        onClick={onUndo}
        disabled={!canUndo}
        className="px-4 py-2 text-xs font-medium rounded transition-colors bg-carbon-side/40 text-neutral/70 hover:bg-carbon-side/60 disabled:opacity-30 disabled:cursor-not-allowed"
      >
        Undo
      </button>
      <button
      type='button'
        onClick={onClear}
        disabled={!canClear}
        className="px-4 py-2 text-xs font-medium rounded transition-colors bg-carbon-side/40 text-neutral/70 hover:bg-carbon-side/60 disabled:opacity-30 disabled:cursor-not-allowed"
      >
        Clear
      </button>*/}
      <button
        type='button'
        onClick={onRecenter}
        className="px-4 py-2 text-xs font-medium rounded transition-colors bg-carbon-side/40 text-neutral/70 hover:bg-carbon-side/60"
      >
        Recenter
      </button>
    </div>
  );
}
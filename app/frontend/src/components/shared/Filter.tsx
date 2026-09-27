import React from 'react';

interface StatusFilterProps<T extends string> {
    readonly options: readonly T[];
    readonly filter: T;
    readonly onChange: (filter: T) => void;
}

export function StatusFilter<T extends string>({ options, filter, onChange }: StatusFilterProps<T>) {
  return (
    <div className="flex gap-2 mb-2">
      {options.map((filt) => (
        <button
          type="button"
          key={filt}
          onClick={() => onChange(filt)}
          className={`text-xs px-4 py-1.5 font-semibold rounded-full border transition-colors uppercase ${filter === filt ? 'bg-torch/25 text-flare border-ignite/40' : 'border-carbon-card text-text-primary hover:bg-smoke-hover'}`}
        >
          {filt}
        </button>
      ))}
    </div>
  );
}

import React from 'react';
import { RoleStatus } from '../../types/RoleRequest';

type FilterOption = 'All' | RoleStatus;

interface RoleFilterTabsProps {
  filter: FilterOption;
  onChange: (filter: FilterOption) => void;
}

const filters: FilterOption[] = ['All', 'pending', 'approved', 'rejected', 'revoked'];

export function RoleFilterTabs({ filter, onChange }: RoleFilterTabsProps) {
  return (
    <div className='overflow-x-auto -mx-3 px-3 md:mx-0 md:px-0 mb:-4'>
      <div className="flex gap-2 mb-4">
        {filters.map((fil) => (
          <button
            type="button"
            key={fil}
            onClick={() => onChange(fil)}
            className={`text-xs font-semibold px-4 py-1.5 rounded-full border transition-colors capitalize ${filter === fil ? 'bg-ignite/20 text-flare border-ignite/30' : 'border-carbon-card text-text-primary/50 hover:bg-smoke-hover'}`}
          >
            {fil}
          </button>
        ))}
      </div>
    </div>
  );
}

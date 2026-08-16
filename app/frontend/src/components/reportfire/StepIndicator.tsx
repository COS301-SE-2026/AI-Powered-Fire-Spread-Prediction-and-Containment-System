import React from 'react';
import { StepBadge } from './StepBadge';

export default function StepIndicator() {
  return (
    <ol className="flex items-center gap-6 flex-wrap text-body text-text-primary">
      <li className="flex items-center gap-2">
        <StepBadge number={1} />
        Drop a pin on the map
      </li>
      <li className="flex items-center gap-2">
        <StepBadge number={2} />
        Drag boundary ring to show size
      </li>
      <li className="flex items-center gap-2">
        <StepBadge number={3} />
        Add details and submit
      </li>
    </ol>
  );
}

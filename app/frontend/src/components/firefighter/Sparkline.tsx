import React from "react";

export function Sparkline({ values }: {values: number[]}) {
  if (values.length < 2) return null;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const pts = values.map((v, i) => `${(i / (values.length - 1)) * 100}, ${28 - ((v - min) / range) * 26}`).join(' ');

  return (
    <svg viewBox='0 0 100 30' preserveAspectRatio='none' className='w-full h-7'>
      <polyline
        points={pts}
        fill='none'
        stroke='#fe8024'
        strokeWidth={1.5}
        vectorEffect='non-scaling-stroke'
      />
    </svg>
  )
}
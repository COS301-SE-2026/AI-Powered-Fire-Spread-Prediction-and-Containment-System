import React from 'react';

const COL_SPAN_CLASSES: Record<number, string> = {
  6: 'xl:col-span-6',
  7: 'xl:col-span-7',
  8: 'xl:col-span-8',
  9: 'xl:col-span-9',
};

const HEIGHT_CLASSES: Record<string, string> = {
  sm: 'h-[30rem]',
  md: 'h-[40rem]',
  lg: 'h-[46rem]',
};

interface MapPanelProps {
  children: React.ReactNode;
  colSpan?: number; // Grd col span at xl breakpoint. Defaults to 8 (pairs with a 4-col side panel)
  height?: keyof typeof HEIGHT_CLASSES; // Panel height preset. Defaults to lg
}

export function MapPanel({ children, colSpan = 8, height = 'lg' }: Readonly<MapPanelProps>) {
  const colSpanClass = COL_SPAN_CLASSES[colSpan] ?? COL_SPAN_CLASSES[8];
  const heightClass = HEIGHT_CLASSES[height] ?? HEIGHT_CLASSES.lg;

  return (
    <div className={`${colSpanClass} flex flex-col gap-6`}>
      <div
        className={`relative rounded-2xl overflow-hidden border border-surface-card ${heightClass} w-full shadow-md`}
      >
        {children}
      </div>
    </div>
  );
}

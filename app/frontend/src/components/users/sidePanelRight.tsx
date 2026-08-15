import React from 'react';

const COL_SPAN_CLASSES: Record<number, string> = {
  3: 'xl:col-span-3',
  4: 'xl:col-span-4',
  5: 'xl:col-span-5',
  6: 'xl:col-span-6',
};

interface SidePanelRightProps {
  title: string; // Required
  children: React.ReactNode; // Required
  maxHeight?: string; // Optional: max heigh for scroll panel body
  colSpan?: number; // Optional: Grid col span set at xl breakpoint. Defaults to 4 (pairs with an 8-col mapPanel)
}

export function SidePanelRight({
  title,
  children,
  maxHeight,
  colSpan = 4,
}: Readonly<SidePanelRightProps>) {
  const colSpanClass = COL_SPAN_CLASSES[colSpan] ?? COL_SPAN_CLASSES[4];

  return (
    <div className={`${colSpanClass} flex flex-col gap-3`}>
      <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase shrink-0">
        {title}
      </h2>
      <div
        className="rounded-2xl bg-surface-sidebar/40 backdrop-blur-md border border-surface-card overflow-y-auto"
        style={{ maxHeight }}
      >
        {children}
      </div>
    </div>
  );
}

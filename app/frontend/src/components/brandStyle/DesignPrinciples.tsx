import React from 'react';

export default function DesignPrinciplesSection() {
  return (
    <div className="flex flex-col gap-4">
      <p className="max-w-2xl text-lg font-light leading-relaxed text-text-muted font-body">
        These principles serve as the operational foundation for Fireaway. By prioritizing
        high-performance reliability and clarity, we ensure that every interface decision
        empowers responders to make life-saving decisions with speed, accuracy, and absolute
        confidence.
      </p>

    <h2 className="mb-0.5 font-mono text-lg font-semibold uppercase tracking-widest text-text-muted">Core Principles</h2>
      <div className="grid grid-cols-1 gap-4 w-full">
        <div className="rounded-md border border-carbon-stroke p-6">
          <p className="mb-2 font-display text-xl font-bold text-text-primary">
            Consistency
          </p>
          <p className="text-base text-text-primary font-body">
            The application of unified interaction patterns, component libraries, and standardized terminology across all interfaces to minimize cognitive load and maximize efficiency.
          </p>
        </div>

        <div className="rounded-md border border-carbon-stroke p-6">
          <p className="mb-2 font-display text-xl font-bold text-text-primary">
            Simplicity
          </p>
          <p className="text-base text-text-primary font-body">
            The prioritization of removal of non-essential elements, ensuring that every component directly supports tactical decision-making.
          </p>
        </div>

        <div className="rounded-md border border-carbon-stroke p-6">
          <p className="mb-2 font-display text-xl font-bold text-text-primary">
            Responsiveness
          </p>
          <p className="text-base text-text-primary font-body">
            The capability of the interface to dynamically adapt its layout and functionality across varying display resolutions.
          </p>
        </div>
      </div>
    </div>
  );
}
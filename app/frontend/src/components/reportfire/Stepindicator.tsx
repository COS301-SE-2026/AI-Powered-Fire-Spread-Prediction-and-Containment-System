// components/StepIndicator.tsx
// ─────────────────────────────────────────────────────────────
// Static numbered instruction steps shown above the map.
// ─────────────────────────────────────────────────────────────

type Step = {
  label: string;
};

type Props = {
  steps: Step[];
};

export default function StepIndicator({ steps }: Props) {
  return (
    <ol className="flex items-center gap-6 flex-wrap">
      {steps.map((step, i) => {
        return (
          <li key={i} className="flex items-center gap-2.5">
            {/* Numbered Badge - Using solid Ignite Orange matching theme metrics */}
            <span
              className="inline-flex items-center justify-center w-5 h-5 rounded-full text-[11px] font-bold shrink-0 bg-[var(--color-ignite)] text-[var(--color-primary-content)]"
            >
              {i + 1}
            </span>

            {/* Label - Using clear, crisp white typography */}
            <span
              className="text-xs md:text-sm font-semibold tracking-wide font-[var(--font-body)] text-[var(--color-primary-content)]"
            >
              {step.label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
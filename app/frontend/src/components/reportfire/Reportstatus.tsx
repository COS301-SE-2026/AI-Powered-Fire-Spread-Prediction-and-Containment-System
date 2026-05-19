// components/ReportStatus.tsx
// ─────────────────────────────────────────────────────────────
// Vertical dot-connector timeline showing the lifecycle of a
// submitted fire report.
// ─────────────────────────────────────────────────────────────

type StatusStep = {
  label:  string;
  detail: string;
};

type Props = {
  steps?:       StatusStep[];
  activeIndex?: number; // furthest completed step (0-based), -1 = none
};

const DEFAULT_STEPS: StatusStep[] = [
  { label: "Report submitted",     detail: "Ref #FW-200260503-45678 assigned"      },
  { label: "Pending", detail: "Started verification process"         },
  { label: "Verified",             detail: "Push notifications sent out"          },
  { label: "Notified of outcome",  detail: "You will receive a notification if you are a registered user." },
];

export default function ReportStatus({ steps = DEFAULT_STEPS, activeIndex = -1 }: Props) {
  return (
    <section>
      <h2
        className="text-xl font-bold mb-4"
        style={{ fontFamily: "var(--font-display)", color: "var(--color-primary-content)" }}
      >
        Report Status
      </h2>

      <ol className="flex flex-col">
        {steps.map((step, i) => {
          const isDone = i <= activeIndex;
          const isLast = i === steps.length - 1;

          return (
            <li key={i} className="flex gap-3">

              {/* Dot + connector line */}
              <div className="flex flex-col items-center">
                <span
                  className="w-3 h-3 rounded-full mt-0.5 shrink-0 transition-colors"
                  style={{
                    background: isDone ? "var(--color-ignite)" : "var(--color-carbon-input)",
                    boxShadow:  isDone ? "0 0 6px var(--color-ignite)" : "none",
                  }}
                />
                {!isLast && (
                  <span
                    className="w-px flex-1 mt-1 mb-1"
                    style={{ background: "var(--color-carbon-input)" }}
                  />
                )}
              </div>

              {/* Text */}
              <div className="pb-4">
                <p
                  className="text-sm font-semibold leading-none"
                  style={{
                    color: isDone ? "#ffffff" : "rgba(255,255,255,0.3)",
                    fontFamily: "var(--font-body)",
                  }}
                >
                  {step.label}
                </p>
                <p
                  className="text-[11px] mt-1 leading-snug"
                  style={{ color: isDone ? "rgba(255,255,255,0.45)" : "rgba(255,255,255,0.2)" }}
                >
                  {step.detail}
                </p>
              </div>

            </li>
          );
        })}
      </ol>
    </section>
  );
}
import React from "react";

type StatusStep = {
    label: string;
    detail: string;
};

type Props = {
    steps?: StatusStep[];
    activeIndex?: number; 
    currentRef?: string;  
};

const DEFAULT_STEPS: StatusStep[] = [
    { label: "Report submitted",    detail: "Ref #FW-PENDING assigned" },
    { label: "Pending",             detail: "Started verification process" },
    { label: "Verified",            detail: "Push notifications sent out" },
    { label: "Notified of outcome", detail: "You will receive a notification if you are a registered user." },
];

export default function ReportStatus({ steps = DEFAULT_STEPS, activeIndex = -1, currentRef }: Props) {
    // Inject the dynamically generated transaction reference ID string safely into index[0] layout map
    const processedSteps = steps.map((step, idx) => {
        if (idx === 0 && currentRef) {
            return { ...step, detail: `Ref #${currentRef} assigned` };
        }
        return step;
    });

    return (
        <section>
            <h2
                className="text-xl font-bold mb-4"
                style={{ fontFamily: "var(--font-display)", color: "var(--color-primary-content)" }}
            >
                Report Status
            </h2>

            <ol className="flex flex-col">
                {processedSteps.map((step, i) => {
                    const isDone = i <= activeIndex;
                    const isLast = i === processedSteps.length - 1;

                    return (
                        <li key={i} className="flex gap-3">
                            
                            {/* Dot + connector line */}
                            <div className="flex flex-col items-center">
                                <span
                                    className="w-3 h-3 rounded-full mt-0.5 shrink-0 transition-colors"
                                    style={{
                                        background: isDone ? "var(--color-ignite)" : "var(--color-carbon-input)",
                                        boxShadow: isDone ? "0 0 6px var(--color-ignite)" : "none",
                                    }}
                                />
                                {!isLast && (
                                    <span
                                        className="w-px flex-1 mt-1 mb-1"
                                        style={{ background: "var(--color-carbon-input)" }}
                                    />
                                )}
                            </div>

                            {/* Text Frame */}
                            <div className="pb-4">
                                <p
                                    className="text-sm font-semibold leading-none"
                                    style={{
                                        color: isDone ? "var(--color-primary-content)" : "rgba(255,255,255,0.3)",
                                        fontFamily: "var(--font-body)",
                                    }}
                                >
                                    {step.label}
                                </p>
                                <p
                                    className="text-[11px] mt-1 leading-snug"
                                    style={{ 
                                        color: isDone ? "rgba(255,255,255,0.45)" : "rgba(255,255,255,0.2)",
                                        fontFamily: "var(--font-body)"
                                    }}
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
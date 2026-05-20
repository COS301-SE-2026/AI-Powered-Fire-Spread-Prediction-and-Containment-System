import React from "react";

type Step = {
    label: string;
};

type Props = {
    steps: Step[];
};

export default function StepIndicator({ steps }: Props) {
    return (
        <ol className="flex items-center gap-6 flex-wrap font-body text-primary-content">
            {steps.map((step, i) => {
                return (
                    <li key={i} className="flex items-center gap-2.5">
                        
                        {/* Numbered Badge */}
                        <span className="inline-flex items-center justify-center w-5 h-5 rounded-full text-[11px] font-bold shrink-0 bg-ignite text-primary-content">
                            {i + 1}
                        </span>

                        {/* Label  */}
                        <span className="text-xs md:text-sm font-semibold tracking-wide">
                            {step.label}
                        </span>

                    </li>
                );
            })}
        </ol>
    );
}
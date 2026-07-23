"use client";

import React from "react";
import { FormError } from "./ReportFormError";

interface DescriptionProps {
    readonly value: string;
    readonly error?: string;
    readonly onChange: (value: string) => void;
}

export function DescriptionField({ value, error, onChange }: DescriptionProps) {
    return (
        <div className="w-full">
            <div className="flex items-baseline gap-2 mb-2">
                <span className="label-text font-semibold ">Description</span>
                <span className="text-xs text-white/40">optional</span>
            </div>
            <textarea
                rows={4}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="E.g., Surface line fire spreading northeast toward residential properties..."
                className="textarea textarea-bordered w-full bg-surface-input border-carbon-stroke focus:outline-ignite resize-none leading-relaxed"/>
            {error && <FormError message={error}/>}
        </div>
    );
}
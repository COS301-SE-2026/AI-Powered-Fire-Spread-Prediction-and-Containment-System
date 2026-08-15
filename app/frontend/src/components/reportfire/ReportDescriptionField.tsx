"use client";

import React, {useId} from "react";
import { Alert } from "../shared/Alerts";

interface DescriptionProps {
    readonly value: string;
    readonly error?: string;
    readonly onChange: (value: string) => void;
}

export function DescriptionField({ value, error = "", onChange }: DescriptionProps) {
    const id = useId();

    return (
        <div className="w-full">
            <div className="flex items-baseline gap-2 mb-2">
                <label htmlFor={id} className="text-lg font-semibold text-white block">Description</label>
                <span className="text-xs text-white/40">optional</span>
            </div>
            <textarea
                id={id}
                rows={4}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="E.g., Surface line fire spreading northeast toward residential properties..."
                className="textarea textarea-bordered w-full bg-surface-input border-carbon-stroke focus:outline-ignite resize-none leading-relaxed"
                aria-invalid={!!error}
                aria-describedby={error ? `${id}-error` : undefined} />
            {error &&  <Alert variant="error" message={error} id={`${id}-error`}/>}
        </div>
    );
}


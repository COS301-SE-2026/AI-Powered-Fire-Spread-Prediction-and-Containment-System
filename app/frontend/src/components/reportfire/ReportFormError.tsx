"use client";

import { AlertTriangle } from "lucide-react";

interface FormErrorProps {
    readonly message: string;
}

export function FormError({ message }: FormErrorProps) {
    return (
        <div role="alert" className="alert alert-error alert-soft text-sm py-1 px-1 mt-0.2">
            <AlertTriangle size={20} />
            <span>{message}</span>
        </div>
    )
}
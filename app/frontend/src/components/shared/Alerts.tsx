"use client";

import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";
import type { LucideIcon } from "lucide-react";

type AlertVariant = "success" | "error" | "warning" | "info";

interface AlertsProps {
    readonly variant: AlertVariant;
    readonly message: string;
    readonly id?: string;
}

export function Alert({ variant, message, id }: AlertsProps) {
    let className = "alert-info";
    let Icon: LucideIcon = Info;

    if (variant === "success") {
        className = "alert-success";
        Icon = CheckCircle2;
    } else if (variant === "error") {
        className = "alert-error";
        Icon = XCircle;
    } else if (variant === "warning") {
        className = "alert-warning";
        Icon = AlertTriangle;
    }
    return (
        <div id={id} role="alert" className={`alert ${className} alert-soft text-sm py-4 px-4`}>
            <Icon size={20} />
            <span>{message}</span>
        </div>
    );
}

Alert.defaultProps ={
    readonly: undefined
};
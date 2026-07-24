import React from "react";

interface StatusProps {
    label: string;
    detail: string;
    Icon: React.ComponentType<{ size?: number; className?: string }>;
    color: string;
    refNumber: string;
    locationText?: string;
};

export function StatusCard({  label, detail, Icon, color, refNumber, locationText }: StatusProps) {
    return (
        <div className="rounded-lg bg-carbon-input border border-carbon-stroke p-2 flex items-center gap-3">
            <Icon size={20} className={`shrink-0 ${color}`}/>
                <div>
                    <p className="text-sm font-semibold text-primary-content flex items-center gap-2">{label} #{refNumber}</p>
                    <p className="text-xs text-neutral">{detail}</p>
                </div>
            </div>
    );
}
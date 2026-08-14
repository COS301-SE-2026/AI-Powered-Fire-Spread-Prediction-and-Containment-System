import React from "react";
import { LucideIcon } from "lucide-react";

interface StatusProps {
    label: string;
    detail: string;
    Icon: LucideIcon;
    color: string;
    refNumber: string;
    locationText?: string;
};

export function StatusCard({  label, detail, Icon, color, refNumber, locationText }: Readonly<StatusProps>) {
  return <div className="rounded-lg bg-carbon-input border border-carbon-stroke p-2 flex items-center gap-3">
            <Icon size={20} className={`shrink-0 ${color}`}/>
                <div>
                    <p className="text-sm font-semibold text-primary-content flex items-center gap-2">{label} #{refNumber}</p>
                    <p className="text-xs text-text-primary">{detail}</p>
                </div>
            </div>
}
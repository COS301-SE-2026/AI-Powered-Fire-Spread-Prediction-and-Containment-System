import React from "react";

interface StatCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
}

export function StatCard({ label, value, icon }: StatCardProps) {
  return <div className="flex items-center gap-2 p-3 rounded-lg bg-carbon-side/60 border border-carbon-stroke">
      <div className="text-ignite">{icon}</div>
      <div>
        <div className="text-sm font-bold">{value}</div>
        <div className="text-xs opacity-50">{label}</div>
      </div>
    </div>
}
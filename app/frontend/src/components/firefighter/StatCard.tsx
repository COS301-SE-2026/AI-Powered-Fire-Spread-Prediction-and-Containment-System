interface StatCardProps {
    label: string;
    value: string;
    icon: React.ReactNode;
    iconColor?: string;
}

export function StatCard({label, value, icon, iconColor = "bg-base-100"}: Readonly<StatCardProps>) {
  return <div className="flex items-center gap-4 p-5 rounded-xl bg-carbon-side/60 backdrop-blur-sm border border-carbon-stroke w-full h-full">
            {/* Icon wrapper */}
            <div className={`size-10 rounded-lg bg-carbon-bg border border-carbon-card flex items-center justify-center shrink-0 ${iconColor}`}>
                {icon}
            </div>

            {/* Text wrapper */}
            <div className="flex flex-col">
                <span className="font-bold text-text-primary text-lg tracking-wide">{value}</span>
                <span className="text-xs text-text-primary/50 font-medium mt-0.5">{label}</span>
            </div>
        </div>
}
import { Thermometer, Wind, Droplets, Flame} from "lucide-react";

interface StatCardProps {
    label: string;
    value: string;
    icon: React.ReactNode;
    iconColor?: string;
}

function StatCard({label, value, icon, iconColor = "bg-base-100"}: StatCardProps) {
    return(
        <div className="flex items-center gap-4 p-5 rounded-xl bg-carbon-side/60 backdrop-blur-sm border border-carbon-stroke w-full h-full">
            {/* Icon wrapper */}
            <div className={`size-10 rounded-lg bg-carbon-bg border border-carbon-card flex items-center justify-center shrink-0 ${iconColor}`}>
                {icon}
            </div>

            {/* Text wrapper */}
            <div className="flex flex-col">
                <span className="font-bold text-neutral text-lg tracking-wide">{value}</span>
                <span className="text-xs text-neutral/50 font-medium mt-0.5">{label}</span>
            </div>
        </div>
    );
}

export function EnvironmentWidgets () {
    return(
        <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
            <StatCard icon={<Wind/>} label = "Wind NW" value = "18 km/h"/>
            <StatCard icon={<Thermometer/>} label = "Temperature" value = "38°C"/>
            <StatCard icon={<Flame/>} label = "Fire Danger" value = "High"/>
            <StatCard icon={<Droplets/>} label = "Humidity" value = "32%"/>
        </div>
    );
}
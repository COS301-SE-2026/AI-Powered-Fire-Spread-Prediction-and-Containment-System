import { Thermometer, Wind, Droplets, Flame} from "lucide-react";
import { useState } from "react";

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

interface EnvironmentVariables{
    readonly wind: number;
    readonly wind_dir: number;
    readonly temperature: number;
    readonly fire_danger: string;
    readonly humidity: number;
}

interface EnvironmentWidgetsProp{
    readonly variables: EnvironmentVariables | null;
}

function WindDirection(degree: number): string {
    switch(true) {
        case degree == 0:
            return "N";
            
        case degree == 90:
            return "E";
            
        case degree == 180:
            return "S";
            
        case degree == 270:
            return "W";
            
        case degree < 90 && degree > 0:
            return "NE";
            
        case degree < 180 && degree > 90:
            return "SE";
            
        case degree < 270 && degree > 180:
            return "SW";
            
        case degree < 360 && degree > 270:
            return "NW";
        default:
            return "W";
    }
}

export function EnvironmentWidgets ({variables}: EnvironmentWidgetsProp) {
    if(!variables){
        return(
            <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
                <div className="col-span-2 flex items-center justify-center text-xs">
                    No environment data was found
                </div>   
            </div>
        )
    }

    const {wind, wind_dir, temperature, fire_danger, humidity} = variables;
    const windDirection = WindDirection(wind_dir);

    return(
        <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
            <StatCard icon={<Wind/>} label ={`Wind ${windDirection} `} value = {`${wind} km/h`}/>
            <StatCard icon={<Thermometer/>} label = "Temperature" value = {`${temperature}°C`}/>
            <StatCard icon={<Flame/>} label = "Fire Danger" value ={fire_danger}/>
            <StatCard icon={<Droplets/>} label = "Humidity" value ={`${humidity}%`}/>
        </div>
    );
}
import { Thermometer, Wind, Droplets, Flame} from "lucide-react";

export function EnviromentWidgets () {
    return(
        <div className="grid grid-cols-2 gap-4 mt-1">

            <div className="flex items-center gap-3">
                <div className="p-2 bg-base-100 rounded-lg text-flare opacity-80">
                    <Wind className="size-4"/>
                </div>
                <div>
                    <p className="font-semibold text-sm">18 km/h</p>
                    <p className="text-[10px] uppercase tracking-wider opacity-50 font medium">Wind</p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <div className="p-2 bg-base-100 rounded-lg text-flare opacity-80">
                    <Thermometer className="size-4"/>
                </div>
                <div>
                    <p className="font-semibold text-sm">28°C</p>
                    <p className="text-[10px] uppercase tracking-wider opacity-50 font medium">Temperature</p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <div className="p-2 bg-base-100 rounded-lg text-flare opacity-80">
                    <Flame className="size-4"/>
                </div>
                <div>
                    <p className="font-semibold text-sm">Extreme</p>
                    <p className="text-[10px] uppercase tracking-wider opacity-50 font medium">Fire Danger</p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <div className="p-2 bg-base-100 rounded-lg text-flare opacity-80">
                    <Droplets className="size-4"/>
                </div>
                <div>
                    <p className="font-semibold text-sm">12%</p>
                    <p className="text-[10px] uppercase tracking-wider opacity-50 font medium">Humidity</p>
                </div>
            </div>
            
        </div>
    );
}
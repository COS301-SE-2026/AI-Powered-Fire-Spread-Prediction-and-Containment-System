import { Thermometer, Wind, Droplets, Flame} from "lucide-react";
import{ StatCard } from './StatCard';

export interface EnvironmentVariables{
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

export function EnvironmentWidgets({variables}: EnvironmentWidgetsProp) {
    if(!variables){
        return(
            <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
                <div className="col-span-2 flex items-center justify-center text-xs">
                    No environment data was found
                </div>
            </div>
        )
    }

    const {wind, wind_dir: windDeg, temperature, fire_danger: fireDanger, humidity} = variables;
    const windDirection = WindDirection(windDeg);

    return(
        <div className="grid grid-cols-2 grid-rows-2 gap-3 h-full">
            <StatCard icon={<Wind/>} label ={`Wind ${windDirection} `} value = {`${wind} km/h`}/>
            <StatCard icon={<Thermometer/>} label = "Temperature" value = {`${temperature}°C`}/>
            <StatCard icon={<Flame/>} label = "Fire Danger" value ={`fireDanger`}/>
            <StatCard icon={<Droplets/>} label = "Humidity" value ={`${humidity}%`}/>
        </div>
    );
}
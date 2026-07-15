import { LayoutDashboard, Flame, Map, BookAlert, ShieldAlert, Settings, Wind, Thermometer, Droplets, UserCircle, LogOut, PlusCircle, AlertTriangle, Radio, Navigation } from 'lucide-react';
import { IconCard } from './iconCard';

export function IconGrid() {
    return (
        <div className="overflow-hidden rounded-md border border-carbon-stroke">
            <div className="font-body text-base leading-relaxed text-smoke">
                <p className="font-body text-base leading-relaxed text-smoke">
                    All icons use the Lucide React library.
                </p>
            </div>
            <div className="grid grid-cols-2 gap-px bg-carbon-stroke sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                <IconCard Icon={LayoutDashboard} name="Dashboard" usage="Dashboard nav" />
                <IconCard Icon={Map} name="Map" usage="Map views" />
                <IconCard Icon={BookAlert} name="BookAlert" usage="Reports" />
                <IconCard Icon={ShieldAlert} name="ShieldAlert" usage="Admin / roles" />
                <IconCard Icon={Settings} name="Settings" usage="System settings" />
                <IconCard Icon={Wind} name="Wind" usage="Wind data" />
                <IconCard Icon={Thermometer} name="Thermometer" usage="Temperature" />
                <IconCard Icon={Droplets} name="Droplets" usage="Humidity" />
                <IconCard Icon={UserCircle} name="UserCircle" usage="User / login" />
                <IconCard Icon={LogOut} name="LogOut" usage="Logout" />
                <IconCard Icon={PlusCircle} name="PlusCircle" usage="Add / report" />
                <IconCard Icon={AlertTriangle} name="AlertTriangle" usage="Danger / hazard" />
                <IconCard Icon={Radio} name="Radio" usage="Comms / dispatch" />
                <IconCard Icon={Navigation} name="Navigation" usage="Location / route" />
            </div>
        </div>
    );
}
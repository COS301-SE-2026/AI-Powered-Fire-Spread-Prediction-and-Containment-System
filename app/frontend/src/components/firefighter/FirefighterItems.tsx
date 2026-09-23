import { Map, Flame, LayoutDashboard, BookAlert, Droplets, Cpu } from 'lucide-react';
import { NavLink } from '../layout/NavLink';

export function FirefighterItems() {
  return (
    <>
      <NavLink icon={LayoutDashboard} label="Firefighter Dashboard" href="/firefighter/dashboard" />
      <NavLink icon={BookAlert} label="Reported Fires" href="/firefighter/reported-fires" />
      <NavLink icon={Flame} label="Report a Fire" href="/firefighter/report-fire" />
      <NavLink icon={Map} label="Fire Simulation AI" href="/firefighter/simulation" />
      <NavLink icon={Droplets} label="Register Resources" href="/firefighter/RegisterResource" />
      <NavLink icon={Cpu} label="Volunteer yout GPU" href="/firefighter/GPUWorkers" />
    </>
  );
}

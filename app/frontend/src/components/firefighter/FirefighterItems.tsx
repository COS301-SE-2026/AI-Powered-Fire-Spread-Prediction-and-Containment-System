import { Map, Flame, Gpu, Play, Droplets, Cpu, CirclePlus } from 'lucide-react';
import { NavLink } from '../layout/NavLink';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';
import { useGPUWorkers } from '../../hooks/useGPUWorkers';

export function FirefighterItems() {
  const { isEligible } = useDeviceCapability();
  const { workers } = useGPUWorkers();
  
  const hasRegisteredMachine = workers && workers.length > 0;
  const shouldShowVolunteerTab = isEligible || hasRegisteredMachine;
  
  return (
    <>
      <NavLink icon={Map} label="Firefighter Dashboard" href="/firefighter/dashboard" />
      <NavLink icon={CirclePlus} label="Report a Fire" href="/firefighter/report-fire" />
      <NavLink icon={Play} label="Fire Simulation AI" href="/firefighter/simulation" />
      <NavLink icon={Droplets} label="Register Resources" href="/firefighter/RegisterResource" />
      {shouldShowVolunteerTab && (
        <NavLink icon={Cpu} label="Volunteer your GPU" href="/firefighter/GpuVolunteer" />
      )}
      <NavLink icon={Gpu} label="GPU Workers" href="/firefighter/GpuWorkers" />
      <NavLink icon={Flame} label="Reported Fires" href="/firefighter/reported-fires" />
    </>
  );
}

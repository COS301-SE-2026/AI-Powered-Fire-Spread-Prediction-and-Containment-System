import React from 'react';
import { Flame, Map, Cpu, Droplets, Play } from 'lucide-react';
import { NavLink } from '../layout/NavLink';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';
import { useGPUWorkers } from '../../hooks/useGPUWorkers';

export function UserItems() {
  const { isEligible } = useDeviceCapability();
  const { workers } = useGPUWorkers();

  const hasRegisteredMachine = workers && workers.length > 0;
  const shouldShowVolunteerTab = isEligible || hasRegisteredMachine;

  return (
    <>
      <NavLink icon={Map} label="Home" href="/users/live-map" />
      <NavLink icon={Flame} label="Report a Fire" href="/users/report-fire" />
      <NavLink icon={Play} label="Fire Simulation AI" href="/users/simulation" />
      <NavLink icon={Droplets} label="Register Resources" href="/users/RegisterResource" />
      {shouldShowVolunteerTab && (
        <NavLink icon={Cpu} label="Volunteer your GPU" href="/users/GpuVolunteer" />
      )}
    </>
  );
}

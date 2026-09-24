import React from 'react';
import { Flame, House, Cpu, Droplets } from 'lucide-react';
import { NavLink } from '../layout/NavLink';
import { useDeviceCapability } from '../../hooks/useDeviceCapability';
import { useGPUWorkers } from '../../hooks/useGPUWorkers';

export function UserItems() {
  const { isEligible } = useDeviceCapability();
  const { workers } = useGPUWorkers

  const hasRegisteredMachine = workers && workers.length > 0;
  const shouldShowVolunteerTab = isEligible || hasRegisteredMachine;

  return (
    <>
      <NavLink icon={House} label="Home" href="/users/live-map" />
      <NavLink icon={Flame} label="Report a Fire" href="/users/report-fire" />
      <NavLink icon={Droplets} label="Register Resources" href="/users/RegisterResource" />
      {shouldShowVolunteerTab && (
        <NavLink icon={Cpu} label="Volunteer your GPU" href="/users/GpuVolunteer" />
      )}
      {/* <NavLink icon={Map} label="Fire Simulation" href="/users/simulation" />
      <NavLink icon={MessageCircleWarning} label="Notifications" href="/users/under-construction" />
      <NavLink icon={MessagesSquare} label="Community" href="/users/under-construction" /> */}
    </>
  );
}

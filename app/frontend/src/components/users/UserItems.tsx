import React from 'react';
import { Map, Flame, House, MessageCircleWarning, MessagesSquare } from 'lucide-react';
import { NavLink } from '../layout/NavLink';

export function UserItems() {
  return (
    <>
      <NavLink icon={House} label="Home" href="/users/live-map" />
      <NavLink icon={Flame} label="Report a Fire" href="/users/report-fire" />
      <NavLink icon={Map} label="Fire Simulation" href="/users/simulation" />
      <NavLink icon={MessageCircleWarning} label="Notifications" href="/users/under-construction" />
      <NavLink icon={MessagesSquare} label="Community" href="/users/under-construction" />
    </>
  );
}

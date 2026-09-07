import React from 'react';
import { Map, LayoutDashboard, ShieldAlert, Flame, TrendingUp, PlusCircle } from 'lucide-react';
import { NavLink } from '../layout/NavLink';

export function AdminItems() {
  return (
    <>
      <NavLink icon={LayoutDashboard} label="Admin Dashboard" href="/admin/dashboard" />
      {/* <NavLink icon={TrendingUp} label="Analytics" href="/admin/analytics" /> */}
      <NavLink icon={Map} label="Live Map" href="/admin/live-map" />
      <NavLink icon={PlusCircle} label="Report a Fire" href="/admin/report-fire" />
      <NavLink icon={ShieldAlert} label="Role Approvals" href="/admin/approvals" />
      <NavLink icon={Flame} label="Reported Fires" href="/admin/reported-fire" />
    </>
  );
}

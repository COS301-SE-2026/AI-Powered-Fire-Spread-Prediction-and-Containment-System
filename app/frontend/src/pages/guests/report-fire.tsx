import { Map, CircleAlert } from 'lucide-react';
import { SideBar } from '../../components/layout/SideBar';
import { NavLink } from '../../components/layout/NavLink';
import ReportPage from '../../components/reportfire/ReportPage';

export default function RegisteredReportFire() {
  const guestNavItems = (
    <>
      <NavLink icon={Map} label="Live Map" href="/guests/live-map" />
      <NavLink icon={CircleAlert} label="Report Fire" href="/guests/report-fire" />
    </>
  );
  return (
    <SideBar items={guestNavItems} hideLogout hideLoginRegister={false}>
      <ReportPage showHeaderIcons={false} />
    </SideBar>
  );
}

import HelpPage from '../../components/shared/HelpMenu';
import { NavLink } from '../../components/layout/NavLink';
import { CircleAlert, Map } from 'lucide-react';
import { SideBar } from '@/components/layout/SideBar';

export default function GuestHelpPage() {
    const guestNavItems = (
    <>
      <NavLink icon={Map} label="Live Map" href="/guests/live-map" />
      <NavLink icon={CircleAlert} label="Report Fire" href="/guests/report-fire" />
    </>
  );

    return (
        <SideBar items={guestNavItems} hideLogout hideLoginRegister={false}>
            <HelpPage />
        </SideBar>
    )
}
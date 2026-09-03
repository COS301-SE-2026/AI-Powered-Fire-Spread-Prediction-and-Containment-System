import { CircleAlert, Map } from 'lucide-react';
import { SideBar } from '@/components/layout/SideBar';
import HelpPage from '../../components/shared/HelpPage';
import { NavLink } from '../../components/layout/NavLink';

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
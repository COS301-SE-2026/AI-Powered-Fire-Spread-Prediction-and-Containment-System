'use client';

import dynamic from 'next/dynamic';
import { Map, CircleAlert } from 'lucide-react';
import { SideBar } from '../../components/layout/SideBar';
import { NavLink } from '../../components/layout/NavLink';
import { GuestEnvironment } from '../../components/guest/GuestEnvironment';
import { GuestReports } from '../../components/guest/GuestReports';
import { GuestActions } from '../../components/guest/GuestActions';
import { useGuestDashboard } from '../../hooks/useGuestDashboard';
import { PageHeader } from '../../components/layout/pageHeader';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';
import { useFireSelect } from '../../hooks/useFireSelectGuest';

const PublicFireMap = dynamic(
  () => import('../../components/firefighter/FireMap').then((mod) => mod.FireMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex-1 flex items-center justify-center h-full w-full">
        <span className="loading loading-spinner loading-lg text-primary" />
      </div>
    ),
  }
);

export default function GuestPublicDashboard() {
  const { location, environmentVariables, reports, recenter } = useGuestDashboard(20);
  const { fireId, handleSelectFire, clearSelect } = useFireSelect();

  const guestNavItems = (
    <>
      <NavLink icon={Map} label="Live Map" href="/guests/live-map" />
      <NavLink icon={CircleAlert} label="Report Fire" href="/guests/report-fire" />
    </>
  );

  return (
    <SideBar items={guestNavItems} hideLogout hideLoginRegister={false}>
      <div className="flex flex-col px-1 py-1 sm:px-1 sm:py-1 lg:px-6 lg:py-6">
        {/* Header */}
        <NotificationToastHost />
        <PageHeader title="Incident Map" subtitle="Public Fire Map View" showIcons={false} />

        {/* Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-3 lg:gap-6">
          {/* Left column */}
          <div className="xl:col-span-7 flex flex-col gap-3 lg:gap-6">
            <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-96 sm:h-104 lg:h-132 w-full shadow-md">
              <PublicFireMap
                lat={location.lat}
                lng={location.lng}
                drawMode={false}
                onDrawComplete={() => {}}
                clearDrawings={0}
                selectedFireId={fireId}
                onSelectFire={handleSelectFire}
                onDeselect={clearSelect}
              />
            </div>
            <div className="grid grid-col gap-2 lg:grid lg:grid-cols-2 lg:gap-3">
              <GuestEnvironment data={environmentVariables} />
              <GuestActions onRecenter={recenter} />
            </div>
          </div>

          {/* Right column – Nearby Reports */}
          <div className="xl:col-span-4 flex flex-col gap-3 h-full">
            <h4 className=" text-text-muted uppercase">
              Nearby Reports
            </h4>
            <div
              className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto max-h-96 lg:max-h-152"
            >
              <GuestReports reports={reports} selectedFireId={fireId} onSelectFire={handleSelectFire}/>
            </div>
          </div>
        </div>
      </div>
    </SideBar>
  );
}

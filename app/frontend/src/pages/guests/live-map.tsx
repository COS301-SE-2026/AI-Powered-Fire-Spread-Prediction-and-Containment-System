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

  const guestNavItems = (
    <>
      <NavLink icon={Map} label="Live Map" href="/guests/live-map" />
      <NavLink icon={CircleAlert} label="Report Fire" href="/guests/report-fire" />
    </>
  );

  return (
    <SideBar items={guestNavItems} hideLogout>
      <div className="flex flex-col p-6">
        {/* Header */}
        <NotificationToastHost />
        <PageHeader title="Incident Map" subtitle="Public Fire Map View" showIcons={false} />

        {/* Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Left column */}
          <div className="xl:col-span-7 flex flex-col gap-6">
            <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-[33rem] w-full shadow-md">
              <PublicFireMap
                lat={location.lat}
                lng={location.lng}
                drawMode={false}
                onDrawComplete={() => {}}
                clearDrawings={0}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <GuestEnvironment data={environmentVariables} />
              <GuestActions onRecenter={recenter} />
            </div>
          </div>

          {/* Right column – Nearby Reports */}
          <div className="xl:col-span-4 flex flex-col gap-3">
            <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase">
              Nearby Reports
            </h2>
            <div
              className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto"
              style={{ maxHeight: 'calc(480px + 2rem + 140px)' }}
            >
              <GuestReports reports={reports} />
            </div>
          </div>
        </div>
      </div>
    </SideBar>
  );
}

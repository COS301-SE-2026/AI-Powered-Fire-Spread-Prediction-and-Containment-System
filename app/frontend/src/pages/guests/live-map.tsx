'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import React, { useState } from 'react';
import { Map, CircleAlert, Plus, LocateFixed } from 'lucide-react';
import { SideBar } from '../../components/layout/SideBar';
import { NavLink } from '../../components/layout/NavLink';
import { GuestEnvironment } from '../../components/guest/GuestEnvironment';
import { useFireSelect } from '../../hooks/useFireSelect';
import { useGuestDashboard } from '../../hooks/useGuestDashboard';
import { PageHeader } from '../../components/layout/pageHeader';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';
import { NearbyReports } from '../../components/shared/nearbyReports';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { useMapLink } from '../../hooks/useMapLink';


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
  const { fireLocation, handleSelectFire, clearSelect } = useFireSelect();
  const [recenterCount, setRecenterCount] = useState(0);
  const { userLocation, nearbyFires } = useNearbyFires();

  useMapLink(handleSelectFire);

  const handleRecenter = () => {
    recenter();
    setRecenterCount((c) => c + 1);
  };

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
          <div className="xl:col-span-8 flex flex-col gap-3 lg:gap-6">
            <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-125 sm:h-104 md:h-120 lg:h-137 w-full shadow-md">
              <PublicFireMap
                lat={location.lat}
                lng={location.lng}
                drawMode={false}
                onDrawComplete={() => {}}
                clearDrawings={0}
                recenter={recenterCount}
                selectedFireId={fireLocation}
                onSelectFire={handleSelectFire}
                onDeselect={clearSelect}
                selectedFireLocation={fireLocation}
              />

              {/* action buttons */}
              <div className='absolute top-3 left-3 z-20 flex flex-col gap-2'>
                <Link href='/guests/report-fire' aria-label='Report a fire' title='Report a fire' className='w-10 h-10 rounded-full bg-primary text-text-primary flex items-center justify-center shadow-lg ring-lg ring-black/10 hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-150'>
                  <Plus className='w-5 h-5' />
                </Link>
                <button type='button' onClick={handleRecenter} aria-label='Recenter map' title='Recenter map' className='w-10 h-10 rounded-full bg-carbon-bg/90 border border-carbon-card text-text-primary flex items-center justify-center shadow-lg backdrop-blur-sm hover:bg-carbon-side hover:scale-105 active:scale-95 transition-all duration-150'>
                  <LocateFixed className='w-5 h-5' />
                </button>
              </div>

              <div className="absolute bottom-0 inset-x-0 z-10 bg-carbon-bg/70 backdrop-blur-md border-t border-carbon-card p-2">
                <GuestEnvironment data={environmentVariables} />
              </div>
            </div>
          </div>

          {/* Right column – Nearby Reports */}
          <div className="xl:col-span-4 flex flex-col gap-3">
            <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase">
              Nearby Reports
            </h2>
            <div
              className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto max-h-130">
              <NearbyReports nearbyFires={nearbyFires}  selectedFireId={fireLocation} onSelectFire={handleSelectFire}/>
            </div>
          </div>
        </div>
      </div>
    </SideBar>
  );
}

import React from 'react';
import dynamic from 'next/dynamic';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { NearbyReports } from '../shared/nearbyReports';
import { PageHeader } from '../layout/pageHeader';

const PublicFireMap = dynamic(() => import('../firefighter/FireMap').then((mod) => mod.FireMap), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center h-full w-full">
      <span className="loading loading-spinner loading-lg text-primary" />
    </div>
  ),
});

export default function MapView() {
  const { userLocation, nearbyFires } = useNearbyFires();
  return (
    <div className="flex flex-col p-6">
      {/* Public View Header */}
      <PageHeader title="Incident Map" subtitle="Public Fire Map View" showIcons />

      {/* Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        <div className="xl:col-span-8 flex flex-col gap-6">
          {/* Map */}
          <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-[40rem] w-full shadow-md">
            <PublicFireMap
              lat={userLocation.lat}
              lng={userLocation.lng}
              drawMode={false}
              onDrawComplete={() => {}}
              clearDrawings={0}
            />
          </div>
        </div>

        {/* Right Column Area (span-4: Scrolling Incident Feed Records) */}
        <div className="xl:col-span-4 flex flex-col gap-3">
          <h2 className="text-xs font-bold tracking-widest text-text-primary/50 uppercase shrink-0">
            Nearby Reports
          </h2>

          {/* Enforces strict scrolling constraints tailored to Ryan's height layout tree */}
          <div
            className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto"
            style={{ maxHeight: 'calc(480px + 2rem + 140px)' }}
          >
            <NearbyReports nearbyFires={nearbyFires} />
          </div>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import dynamic from 'next/dynamic';
import { useFireSelect } from '@/hooks/useFireSelect';
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
  const{ fireLocation, handleSelectFire, clearSelect } = useFireSelect();
  return (
    <div className="flex flex-col p-2">
      {/* Public View Header */}
      <PageHeader title="Incident Map" subtitle="Public Fire Map View" showIcons />

      {/* Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        <div className="xl:col-span-7 flex flex-col gap-6">
          {/* Map */}
          <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-96 sm:h-104 lg:h-132 w-full shadow-md">
            <PublicFireMap
              lat={userLocation.lat}
              lng={userLocation.lng}
              drawMode={false}
              onDrawComplete={() => {}}
              clearDrawings={0}
              selectedFireLocation={fireLocation}
              onSelectFire={handleSelectFire}
              onDeselect={clearSelect}
            />
          </div>
        </div>

        {/* Right Column Area (span-4: Scrolling Incident Feed Records) */}
        <div className="xl:col-span-4 flex flex-col gap-3">
          <h4 className="tracking-widest text-text-muted uppercase">
            Nearby Reports
          </h4>

          {/* Enforces strict scrolling constraints tailored to Ryan's height layout tree */}
          <div
            className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto"
            style={{ maxHeight: 'calc(480px + 2rem + 140px)' }}
          >
            <NearbyReports nearbyFires={nearbyFires}  selectedFireId={fireLocation} onSelectFire={handleSelectFire}/>
          </div>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, LocateFixed } from 'lucide-react';
import dynamic from 'next/dynamic';
import { useMapLink } from '@/hooks/useMapLink';
import { useFireSelect } from '../../hooks/useFireSelect';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { useNearbyResources } from '../../hooks/useNearbyResources';
import { NearbyReports } from '../shared/nearbyReports';
import { NearbyResources } from '../shared/NearbyResources';
import { ResourceMapLegend } from '../shared/ResourceMapLegend';
import { PageHeader } from '../layout/pageHeader';
import { GuestEnvironment } from './GuestEnvironment';
import { useGuestDashboard } from '../../hooks/useGuestDashboard';

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
  const { location, environmentVariables, recenter } = useGuestDashboard(20);
  const { fireLocation, handleSelectFire, clearSelect } = useFireSelect();
  const [recenterCount, setRecenterCount] = useState(0);
  const [showWater, setShowWater] = useState(true);

  const { nearbyResources } = useNearbyResources(userLocation ?? location);
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);
  const [showResources, setShowResources] = useState(true);

  const availableResources = nearbyResources.filter((r) => r.status === 'available');

  function handleSelectResource(r: { id: string }) {
    setSelectedResourceId(r.id);
    setShowResources(true);
  }

  const handleRecenter = () => {
    recenter();
    setRecenterCount((c) => c + 1);
  };
  useMapLink(handleSelectFire);

  const currentLat = userLocation?.lat ?? location?.lat;
  const currentLng = userLocation?.lng ?? location?.lng;

  return (
    <div className="flex flex-col p-2">
      {/* Public View Header */}
      <PageHeader title="Incident Map" subtitle="Public Fire Map View" showIcons />

      {/* Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-8 flex flex-col gap-6">
          {/* Show water toggle above map */}
          <div className='flex justify-end'>
              <label className='flex items-center gap-2 cursor-pointer select-none bg-carbon-bg/90 border border-carbon-card rounded-full px-3 py-1.5 shadow-lg backdrop-blur-sm'>
                <span className='text-sm font-medium text-text-muted'>
                  Show Water
                </span>
                <button
                  type='button'
                  role='switch'
                  aria-checked={showWater}
                  onClick={() => setShowWater((w) => !w)}
                  className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${showWater ? 'bg-ignite' : 'bg-carbon-stroke'}`}
                >
                  <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-md transition-transform ${showWater ? 'translate-x-4' : 'translate-x-1'}`} />
                </button>
              </label>
            </div>
          {/* Map */}
          <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-96 sm:h-104 lg:h-140 w-full shadow-md">
            <PublicFireMap
              lat={currentLat}
              lng={currentLng}
              drawMode={false}
              onDrawComplete={() => {}}
              clearDrawings={0}
              recenter={recenterCount}
              selectedFireLocation={fireLocation}
              onSelectFire={handleSelectFire}
              onDeselect={clearSelect}
              selectedFireId={fireLocation}
              resources={availableResources}
              showResources={showResources}
              selectedResourceId={selectedResourceId}
              onSelectResource={handleSelectResource}
            />
          <div className='absolute top-3 left-3 z-20 flex flex-col gap-2'>
              <Link href='/admin/report-fire' aria-label='Report a fire' title='Report a fire' className='w-10 h-10 rounded-full bg-primary text-text-primary flex items-center justify-center shadow-lg ring-lg ring-black/10 hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-150'>
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
          <ResourceMapLegend />
        </div>

        {/* Right Column Area (span-4: Scrolling Incident Feed Records) */}
        <div className="xl:col-span-4 flex flex-col gap-3 xl:h-150">
          <h4 className="tracking-widest text-text-muted uppercase shrink-0">
            Nearby Reports
          </h4>

          {/* Enforces strict scrolling constraints tailored to Ryan's height layout tree */}
          <div
            className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto max-h-130">
            <NearbyReports nearbyFires={nearbyFires}  selectedFireId={fireLocation} onSelectFire={handleSelectFire}/>
          </div>

          <h4 className="tracking-widest text-text-muted uppercase shrink-0">
            Available Resources
          </h4>
          <div className="max-h-64 xl:max-h-none xl:flex-1 xl:min-h-0 rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto">
            <NearbyResources resources={availableResources}  selectedResourceId={selectedResourceId} onSelectResource={(r) => setSelectedResourceId(r.id)}/>
          </div>
        </div>
      </div>
    </div>
  );
}

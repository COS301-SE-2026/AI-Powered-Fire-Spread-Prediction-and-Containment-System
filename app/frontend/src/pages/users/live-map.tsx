import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, LocateFixed } from 'lucide-react';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { NearbyReports } from '../../components/shared/nearbyReports';
import { UserSideBar } from '../../components/users/UserSideBar';
import { PageHeader } from '../../components/layout/pageHeader';
import { MapPanel } from '../../components/users/mapPanel';
import { SidePanelRight } from '../../components/users/sidePanelRight';
import { FireMap } from '../../components/shared/DynamicFirefighterMap';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';
import { useMapLink } from '../../hooks/useMapLink';
import { useFireSelect } from '../../hooks/useFireSelect';
import { useGuestDashboard } from '../../hooks/useGuestDashboard';
import { GuestEnvironment } from '../../components/guest/GuestEnvironment';

export default function RegisteredUserDashboard() {
  const { userLocation, nearbyFires } = useNearbyFires();
  const { fireLocation, handleSelectFire, clearSelect } = useFireSelect();
  const { environmentVariables, recenter } = useGuestDashboard(20);
  const [recenterCount, setRecenterCount] = useState(0);

  const handleRecenter = () => {
      recenter();
      setRecenterCount((c) => c + 1);
  };

  useMapLink(handleSelectFire);
  return (
    <UserSideBar>
      <div className="flex flex-col p-6">
        <NotificationToastHost />
        <PageHeader title="Welcome" subtitle="Public Fire Map View" showIcons />

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">
          <MapPanel colSpan={8} height="lg">
            <FireMap
              lat={userLocation.lat}
              lng={userLocation.lng}
              drawMode={false}
              onDrawComplete={() => {}}
              clearDrawings={0}
              recenter={recenterCount}
              selectedFireLocation={fireLocation}
              onSelectFire={handleSelectFire}
              onDeselect={clearSelect}
              selectedFireId={fireLocation}
            />
            {/* action buttons */}
              <div className='absolute top-3 left-3 z-20 flex flex-col gap-2'>
                <Link href='/users/report-fire' aria-label='Report a fire' title='Report a fire' className='w-10 h-10 rounded-full bg-primary text-text-primary flex items-center justify-center shadow-lg ring-lg ring-black/10 hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-150'>
                  <Plus className='w-5 h-5' />
                </Link>
                <button type='button' onClick={handleRecenter} aria-label='Recenter map' title='Recenter map' className='w-10 h-10 rounded-full bg-carbon-bg/90 border border-carbon-card text-text-primary flex items-center justify-center shadow-lg backdrop-blur-sm hover:bg-carbon-side hover:scale-105 active:scale-95 transition-all duration-150'>
                  <LocateFixed className='w-5 h-5' />
                </button>
              </div>
            <div className='absolute bottom-0 inset-x-0 z-10 bg-carbon-bg/70 backdrop-blur-md border-t border-carbon-card p-2'>
              <GuestEnvironment data={environmentVariables} />
            </div>

          </MapPanel>

          <SidePanelRight title="Nearby Reports" colSpan={4} maxHeight="33rem">
            <NearbyReports nearbyFires={nearbyFires} selectedFireId={fireLocation} onSelectFire={handleSelectFire} />
          </SidePanelRight>
        </div>
      </div>
    </UserSideBar>
  );
}

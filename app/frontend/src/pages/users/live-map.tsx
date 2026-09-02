import React from 'react';
import { useNearbyFires } from '../../hooks/useNearbyFires';
import { useFireSelect } from '../../hooks/useFireSelect';
import { NearbyReports } from '../../components/shared/nearbyReports';
import { UserSideBar } from '../../components/users/UserSideBar';
import { PageHeader } from '../../components/layout/pageHeader';
import { MapPanel } from '../../components/users/mapPanel';
import { SidePanelRight } from '../../components/users/sidePanelRight';
import { FireMap } from '../../components/shared/DynamicFirefighterMap';
import { NotificationToastHost } from '../../components/notification/NotificationToastHost';

export default function RegisteredUserDashboard() {
  const { userLocation, nearbyFires } = useNearbyFires();
  const { fireLocation, handleSelectFire, clearSelect } = useFireSelect();

  return (
    <UserSideBar>
      <div className="flex flex-col px-2 py-2 ">
        <NotificationToastHost />
        <PageHeader title="Welcome" subtitle="Public Fire Map View" showIcons />

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-3 lg:gap-6">
          <MapPanel colSpan={8} height="responsive">
            <FireMap
              lat={userLocation.lat}
              lng={userLocation.lng}
              drawMode={false}
              onDrawComplete={() => {}}
              clearDrawings={0}
              selectedFireLocation={fireLocation}
              onSelectFire={handleSelectFire}
              onDeselect={clearSelect}
            />
          </MapPanel>

          <SidePanelRight title="Nearby Reports" colSpan={4} maxHeight="calc(480px + 2rem + 197px)">
            <NearbyReports nearbyFires={nearbyFires} selectedFireId={fireLocation} onSelectFire={handleSelectFire} />
          </SidePanelRight>
        </div>
      </div>
    </UserSideBar>
  );
}

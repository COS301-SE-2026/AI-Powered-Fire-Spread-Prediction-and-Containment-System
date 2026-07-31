import React from 'react';
import { NearbyReports, useNearbyFires} from '../../components/nearbyReports';
import { UserSideBar } from '../../components/users/usersSidebar';
import { PageHeader } from '../../components/pageHeader';
import { MapPanel } from '../../components/users/mapPanel';
import { SidePanelRight } from '../../components/users/sidePanelRight';
import { FireMap } from '../../components/DynamicFirefighterMap';

export default function RegisteredUserDashboard (){
    const { userLocation, nearbyFires } = useNearbyFires();

    return(
        <UserSideBar>
            <div className="flex flex-col p-6">

                <PageHeader
                    title="Welcome"
                    subtitle="Public Fire Map View"
                />

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">
                    <MapPanel colSpan={8} height='lg'>
                        <FireMap lat={userLocation.lat} lng={userLocation.lng} drawMode={false} onDrawComplete={() => {}} clearDrawings={0}/>
                    </MapPanel>

                    <SidePanelRight title="Nearby Reports" colSpan={4} maxHeight="calc(480px + 2rem + 197px)">
                        <NearbyReports nearby_fires={nearbyFires}/>
                    </SidePanelRight>
                </div>
            </div>
        </UserSideBar>
    );
}
import dynamic from 'next/dynamic';
import { NearbyReports } from '../../components/firefighter/nearbyReports';
import { SideBarLayout } from '../../components/demoSidebar';
import { PageHeader } from '../../components/pageHeader';
import { MapPanel } from '../../components/users/mapPanel';
import { SidePanelRight } from '../../components/users/sidePanelRight';

const FireMap = dynamic(
    () => import('../../components/firefighter/FireMap').then((mod) => mod.FireMap),
    {
        ssr: false,
        loading: () => (
            <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
                <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
                    Initializing Map
                </span>
            </div>
        )
    }
);

export default function RegisteredUserDashboard (){
    return(
        <SideBarLayout>
            <div className="flex flex-col p-6">

                <PageHeader
                    title="Welcome"
                    subtitle="Public Fire Map View"
                />

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1">
                    <MapPanel colSpan={8} height='lg'>
                        <FireMap />
                    </MapPanel>

                    <SidePanelRight title="Nearby Reports" colSpan={4} maxHeight="calc(480px + 2rem + 197px)">
                        <NearbyReports />
                    </SidePanelRight>
                </div>
            </div>
        </SideBarLayout>
        
    );
   
}
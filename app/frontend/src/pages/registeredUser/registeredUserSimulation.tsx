import React, { useState } from 'react';
import { SidebarLayout } from '../../components/users/sidebar';
import { NearbyReports, useNearbyFires } from '../../components/nearbyReports';
import Button from '../../components/Button';
import { SystemAlertsPanel} from '../../components/users/SystemAlertsPanel';
import { FireMap } from '../../components/DynamicFiremap';

export default function GuestPublicDashboard() {
    const [isAlertsOpen, setIsAlertsOpen] = useState<boolean>(false);
    const { userLocation, nearbyFires } = useNearbyFires();

    return (
        <SidebarLayout>
            <div className="flex flex-col p-6 relative h-full overflow-hidden">
                
                {/*Public View Header*/}
                <header className="mb-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">
                            Incident Map
                        </h1>
                        <p className="text-sm text-neutral/50 font-medium">
                            Public Fire Map View
                        </p>
                    </div>

                    <Button onClick={() => setIsAlertsOpen(true)}>
                        View Alerts
                    </Button>
                </header>                

                {/*Grid*/}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start h-full pb-10">
                    <div className="xl:col-span-8 flex flex-col gap-6 h-full">
                        
                        {/*Map*/}
                        <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-[50rem] w-full shadow-md">
                            <FireMap lat={userLocation.lat} lng={userLocation.lng} drawMode={false} onDrawComplete={() => {}} clearDrawings={0} />
                        </div>            
                    </div>

                    {/* Right Column Area (span-4: Scrolling Incident Feed Records) */}
                    <div className="xl:col-span-4 flex flex-col gap-3">
                        <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase shrink-0">
                            Nearby Reports
                        </h2>
                        
                        {/* Enforces strict scrolling constraints tailored to Ryan's height layout tree */}
                        <div 
                            className="rounded-2xl bg-carbon-side/40 backdrop-blur-md border border-carbon-card overflow-y-auto" 
                            style={{ maxHeight: 'calc(480px + 2rem + 140px)' }}
                        >
                            <NearbyReports nearby_fires={nearbyFires}/>
                        </div>
                    </div>
                </div>

                <SystemAlertsPanel isOpen={isAlertsOpen} onClose={() => setIsAlertsOpen(false)} />
            </div> 
        </SidebarLayout>
    );
}
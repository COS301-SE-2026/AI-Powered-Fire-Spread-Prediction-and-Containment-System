import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { SidebarLayout } from '../../components/firefighter/sidebar';
import { NearbyReports } from '../../components/NearbyReports';
import { EnvironmentWidgets } from '../../components/WeatherStats';
import Button from '../../components/Button';

const PublicFireMap = dynamic(
    () => import('../../components/firefighter/FireMap').then((mod) => mod.FireMap),
    {
        ssr: false,
        loading: () => (
            <div className="flex-1 flex items-center justify-center bg-carbon-side/20 animate-pulse h-full w-full">
                <span className="text-neutral/40 font-display tracking-widest text-sm uppercase">
                    Initializing Public Map Canvas...
                </span>
            </div>
        )
    }
);

export default function GuestPublicDashboard() {
    const [alertEmail, setAlertEmail] = useState<string>('');
    const [registrationSuccess, setRegistrationSuccess] = useState<boolean>(false);

    const handlePublicRegistration = (e: React.FormEvent) => {
        e.preventDefault();
        if (alertEmail.trim()) {
            setRegistrationSuccess(true);
            setAlertEmail('');
        }
    };

    return (
        <SidebarLayout>
            <div className="flex flex-col p-6">
                
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
                </header>                

                {/*Grid*/}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
                    <div className="xl:col-span-8 flex flex-col gap-6">
                        
                        {/*Map*/}
                        <div className="relative rounded-2xl overflow-hidden border border-carbon-card h-[480px] w-full shadow-md">
                            <PublicFireMap />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 shrink-0">
                            {/*Environmental icons*/}
                            <div className="flex flex-col">
                                <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                                    Environment Variables
                                </h2>
                                <EnvironmentWidgets />
                            </div>

                            {/*Report fire*/}
                            <div className="flex flex-col">
                                <h2 className="text-xs font-bold tracking-widest text-neutral/50 uppercase mb-3">
                                    Public Alert Setup
                                </h2>
                            </div>
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
                            <NearbyReports />
                        </div>
                    </div>
                </div>

            </div> 
        </SidebarLayout>
    );
}
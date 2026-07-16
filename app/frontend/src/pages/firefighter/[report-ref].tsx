import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { FirefighterSideBar } from '../../components/firefighter/firefighterSidebar';
import { ReportDetails } from '../../components/admin/reportDetails';
import { ReportDescription } from '../../components/admin/reportDescription';
import { ReportActions } from '../../components/firefighter/report_actions_firefighter';
import { ReportPhoto } from '../../components/admin/reportPhoto';
import type { ReportModal } from '../../types/firefighter';

import dynamic from 'next/dynamic';

    const ReportMap = dynamic(
        () => import('../../components/admin/reportMapCard').then(mod => mod.ReportMap),
        { ssr: false }
    );

export default function ViewPage() {
    const router = useRouter();
    const { 'report-ref': reportRef } = router.query;

    const [report, setReport] = useState<ReportModal | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!reportRef) return;
        fetch(`/api/firefighter/reported-fires/${reportRef}`)
        .then(res => {
            if (!res.ok) throw new Error("Report not found");
            return res.json();
        })
        .then(data => setReport(data))
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
        
    }, [reportRef]);

    if (loading) return (
        <FirefighterSideBar>
            <div className="p-6">
                <p className="text-text-muted">Loading report...</p>
            </div>
        </FirefighterSideBar>
    );

    if (error || !report) return (
        <FirefighterSideBar>
            <div className="p-6">
                <p className="text-error">{error ?? 'Report not found.'}</p>
            </div>
        </FirefighterSideBar>
    );


    return (
        <FirefighterSideBar>
            <div className="p-6 flex flex-col h-full w-full">
                <header className="mb-6 flex items-start justify-between">
                    <div>
                        <h1 className='uppercase'>Report {report.reference_number}</h1>
                        <p className='text-text-muted'>Viewing fire report details</p>
                    </div>

                    <button onClick={() => router.back()} className="btn btn-sm rounded-lg">Back</button>
                </header>
                {/* 2 cols*/}
                <div className='grid grid-cols-1 lg:grid-cols-12 gap-4 h-full'>
                    {/*left*/}
                    <div className='lg:col-span-6 flex flex-col gap-4'>
                        <div className="relative overflow-hidden h-75 w-full">
                            <ReportMap lat={report.lat} lng={report.lng} />
                        </div>
                        <ReportDetails report={report} />
                    </div>
                    {/*right*/}
                    <div className='lg:col-span-6 flex flex-col gap-4 h-full'>
                        <ReportPhoto report={report} />
                        <ReportDescription report={report} />
                        <ReportActions report_id={report.id} status={report.status} onStatusChange={(updated) => setReport(updated)} />
                    </div>
                </div>

            
            </div>
        </FirefighterSideBar>
    );
}
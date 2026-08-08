import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { ReportDetails } from './reportDetails';
import { ReportDescription } from './reportDescription';
import { ReportActions } from './reportActions';
import { ReportPhoto } from './reportPhoto';
import type { FireReport } from '../../types/Report';

import dynamic from 'next/dynamic';

    const ReportMap = dynamic(
        () => import('./reportMapCard').then(mod => mod.ReportMap),
        { ssr: false }
    );

    interface ViewProps {
        report_ref: string;
    }

export function ViewPage({ report_ref }: Readonly<ViewProps>) {
    const router = useRouter();

    const [report, setReport] = useState<FireReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!report_ref) return;
        fetch(`/api/admin/reported-fires/${report_ref}`)
        .then(res => {
            if (!res.ok) throw new Error("Report not found");
            return res.json();
        })
        .then(data => setReport(data))
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }, [report_ref]);



    if (loading) return (
        <div className="p-6">
            <p className="text-text-muted">Loading report...</p>
        </div>
    );

    if (error || !report) return (
        <div className="p-6">
            <p className="text-error">{error ?? 'Report not found.'}</p>
        </div>
    );


    return (
        <div className="p-6 flex flex-col h-full w-full">
            <header className="mb-3 flex items-start justify-between">
                <div>
                    <h1 className='uppercase'>Report {report.reference_number}</h1>
                    <p className='text-text-muted'>Viewing fire report details</p>
                </div>

                <button type="button" onClick={() => router.back()} className="btn btn-sm btn-outline rounded-lg">Back</button>
            </header>
            {/* 2 cols*/}
            <div className='grid grid-cols-1 lg:grid-cols-12 gap-2 h-full'>
                {/*left*/}
                <div className='lg:col-span-6 flex flex-col gap-3'>
                    <div className="relative overflow-hidden flex-1 w-full">
                        <ReportMap lat={report.lat} lng={report.lng} />
                    </div>
                    <ReportDetails report={report} />
                </div>
                {/*right*/}
                <div className='lg:col-span-6 flex flex-col gap-2 h-full'>
                    <ReportPhoto report={report} />
                    <ReportDescription report={report} />
                    <ReportActions report_ref={report.reference_number} status={report.status} onStatusChange={(updated) => setReport(updated)} />
                </div>
            </div>
        </div>
    );
}
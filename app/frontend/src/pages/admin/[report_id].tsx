import React from 'react';
import { useRouter } from 'next/router';
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportDetails } from '../../components/admin/reportDetails';
import { ReportDescription } from '../../components/admin/reportDescription';
import { ReportActions } from '../../components/admin/reportActions';
import { ReportPhoto } from '../../components/admin/reportPhoto';
import { mockFireReports } from '../../components/admin/mockReports';

import dynamic from 'next/dynamic';


    const ReportMap = dynamic(
        () => import('../../components/admin/reportMapCard').then(mod => mod.ReportMap),
        { ssr: false }
    );

export default function ViewPage() {
    const router = useRouter();
    const { report_id } = router.query;

    const report = mockFireReports.find(report => report.report_id === report_id);

    if (!report) {
        return (
            <SideBarLayout>
                <div className="p-6">
                    <p className="text-error">Report not found.</p>
                </div>
            </SideBarLayout>
        );
    }

    return (
        <SideBarLayout>
            <div className="p-6 flex flex-col h-full w-full">
                <header className="mb-6 flex items-start justify-between">
                    <div>
                        <h1 className='uppercase'>Report {report_id}</h1>
                        <p className='text-text-muted'>Viewing fire report details</p>
                    </div>

                    <button onClick={() => router.back()} className="btn btn-sm rounded-lg">Back</button>
                </header>
                {/* 2 cols*/}
                <div className='grid grid-cols-1 lg:grid-cols-12 gap-4 h-full'>
                    {/*Left*/}
                    <div className='lg:col-span-6 flex flex-col gap-4'>
                        <div className="relative overflow-hidden h-75 w-full">
                            <ReportMap lat={report.lat ?? -26.2041} lng={report.lng ?? 28.0473} />
                        </div>
                        <ReportDetails report={report} />
                    </div>
                    {/*Right*/}
                    <div className='lg:col-span-6 flex flex-col gap-4 h-full'>
                        <ReportPhoto report={report} />
                        <ReportDescription report={report} />
                        <ReportActions report_id={report.report_id} status={report.status} />
                    </div>
                </div>

            
            </div>
        </SideBarLayout>
    );
}
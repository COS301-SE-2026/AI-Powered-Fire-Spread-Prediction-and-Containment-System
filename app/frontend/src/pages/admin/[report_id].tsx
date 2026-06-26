import React from 'react';
import { useRouter } from 'next/router';
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportDetails } from '../../components/admin/reportDetails';
import { ReportDescription } from '../../components/admin/reportDescription';
import { ReportActions } from '../../components/admin/reportActions';
import { ReportPhoto } from '../../components/admin/reportPhoto';
import type { FireReport } from '../../types/report';

import dynamic from 'next/dynamic';


    const ReportMap = dynamic(
        () => import('../../components/admin/reportMapCard').then(mod => mod.ReportMap),
        { ssr: false }
    );

export default function ViewPage() {
    const router = useRouter();
    const { report_id } = router.query;

    const mockFireReports: FireReport[] = [
        {
            report_id: 'FW-2026-0091',
            location: 'Northcliff, JHB',
            status: 'pending',
            size: '2 km',
            reported_at: new Date('2026-06-19T08:14:00'),
            reporter: 'Sipho Ndlovu',
            description: 'Surface fire spreading northeast.',
            lat: -26.1367,
            lng: 27.9727,
        },
        {
            report_id: 'FW-2026-0087',
            location: 'Soweto, JHB',
            status: 'verified',
            size: '5 km',
            reported_at: new Date('2026-06-19T08:07:02'),
            reporter: 'Anonymous',
            lat: -26.2678,
            lng: 27.8587,
        },
        {
            report_id: 'FW-2026-0085',
            location: 'Centurion, PTA',
            status: 'pending',
            size: '1 km',
            reported_at: new Date('2026-06-18T08:21:45'),
            reporter: 'Lerato Botha',
            lat: -25.8601,
            lng: 28.1894,
        },
        {
            report_id: 'FW-2026-0082',
            location: 'Midrand',
            status: 'verified',
            size: '3 km',
            reported_at: new Date('2026-06-18T08:17:30'),
            reporter: 'Anonymous',
            lat: -25.9971,
            lng: 28.1284,
        },
        {
            report_id: 'FW-2026-0079',
            location: 'Krugersdorp',
            status: 'rejected',
            size: '0.5 km',
            reported_at: new Date('2026-06-18T08:14:10'),
            reporter: 'Ruan Venter',
            lat: -26.0865,
            lng: 27.77,
        },
        {
            report_id: 'FW-2026-0076',
            location: 'Roodepoort',
            status: 'pending',
            size: '4 km',
            reported_at: new Date('2026-06-18T08:11:55'),
            reporter: 'Amahle Dlamini',
            lat: -26.1625,
            lng: 27.8727,
        },
        {
            report_id: 'FW-2026-0073',
            location: 'Alexandra, JHB',
            status: 'verified',
            size: '1.5 km',
            reported_at: new Date('2026-06-18T08:09:20'),
            reporter: 'Anonymous',
            lat: -26.105,
            lng: 28.0922,
        },
    ];

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
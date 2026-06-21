import React, { useState } from 'react';
import type { FireReport, ReportStatus } from '../../types/report';
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportFilterTabs } from '../../components/admin/reportFilter';
import { FireReportsTable } from '../../components/admin/reportTable';
import { SearchBar } from '../../components/admin/searchBar';

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
        lng: 27.9654,
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
        lng: 27.7700,
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
        lat: -26.1050,
        lng: 28.0922,
    },
];

export default function ReportedFiresPage() {
    const [selectedReport, setSelectedReport] = useState<FireReport | null>(null);
    const [filter, setFilter] = useState<'All' | ReportStatus>('All');
    const [search, setSearch] = useState('');
    
    const filteredReports = mockFireReports.filter(report =>
        report.location.toLowerCase().includes(search.toLowerCase()) ||
        report.report_id.toLowerCase().includes(search.toLowerCase()) ||
        report.reporter.toLowerCase().includes(search.toLowerCase())
    );

    return(
        <SideBarLayout>
            <div className="p-6 flex flex-col h-full w-full">
                {/* Header + filter */}
                <header className="mb-6">
                    <h1 className="uppercase">Reported Fires</h1>
                    <p className="text-text-muted">Manage and review fire reports</p>
                </header>

                <div className="flex items-center justify-between mb-4">
                    <ReportFilterTabs filter={filter} onChange={setFilter}/>
                    <div className="flex items-center gap-2">
                        <SearchBar value={search} onChange={setSearch} placeholder="Search by location, ref, reporter..."/>
                    </div> 
                </div>

                {/* table */}
                <FireReportsTable report={filteredReports} filter={filter} onView={setSelectedReport} />
            </div>
        </SideBarLayout>
    );
}
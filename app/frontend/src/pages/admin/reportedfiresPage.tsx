import React, { useState } from 'react';
import type { FireReport, ReportStatus } from '../../types/report';
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportFilterTabs } from '../../components/admin/reportFilter';
import { FireReportsTable } from '../../components/admin/reportTable';
import { SearchBar } from '../../components/admin/searchBar';
import { mockFireReports } from '../../components/admin/mockReports';

export default function ReportedFiresPage() {
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
                <FireReportsTable report={filteredReports} filter={filter} />
            </div>
        </SideBarLayout>
    );
}
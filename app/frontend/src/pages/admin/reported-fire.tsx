import React, { useState } from 'react';
import type { ReportStatus } from '../../types/Report';
import { AdminSideBar } from '../../components/admin/adminSidebar';
import { ReportFilterTabs } from '../../components/admin/reportFilter';
import { FireReportsTable } from '../../components/admin/reportTable';
import { SearchBar } from '../../components/admin/searchBar';
import { useReportedFires } from '../../hooks/useReportedFires';


export default function ReportedFiresPage() {
    const { reports, loading, error } = useReportedFires();
    const [filter, setFilter] = useState<'All' | ReportStatus>('All');
    const [search, setSearch] = useState('');

    const filteredReports = reports.filter(report =>
        report.location_text.toLowerCase().includes(search.toLowerCase()) ||
        report.id.toLowerCase().includes(search.toLowerCase()) ||
        report.reporter_name.toLowerCase().includes(search.toLowerCase())
    );

    return(
        <AdminSideBar>
            <div className="p-6 flex flex-col h-full w-full">

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

                {error && (
                    <div>
                        {error}
                    </div>
                )}

                {loading ? (
                    <div className="flex justify-center items-center min-h-[40vh]">
                        <span className="loading loading-spinner loading-lg text-primary" />
                    </div>
                ) : (
                    <FireReportsTable report={filteredReports} filter={filter} />
                )}
            </div>
        </AdminSideBar>
    );
}
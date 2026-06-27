import React, { useEffect, useState } from 'react';
import type { FireReport, ReportStatus } from '../../types/report';
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportFilterTabs } from '../../components/admin/reportFilter';
import { FireReportsTable } from '../../components/admin/reportTable';
import { SearchBar } from '../../components/admin/searchBar';
import { apiCall } from '../../lib/api';

export default function ReportedFiresPage() {
    const [reports, setReports] = useState<FireReport[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'All' | ReportStatus>('All');
    const [search, setSearch] = useState('');
    
    useEffect(() => {
        fetch('/api/admin/reported-fires')
        .then(res => {
            if (!res.ok) throw new Error("Failed to load reports");
            return res.json();
        })
        .then(data => setReports(data))
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }, []);

    const filteredReports = reports.filter(report =>
        report.location_text.toLowerCase().includes(search.toLowerCase()) ||
        report.id.toLowerCase().includes(search.toLowerCase()) ||
        report.reporter_name.toLowerCase().includes(search.toLowerCase())
    );

    return(
        <SideBarLayout>
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
                    <div>
                        Loading reports...
                    </div>
                ) : (
                    <FireReportsTable report={filteredReports} filter={filter} />
                )}
            </div>
        </SideBarLayout>
    );
}
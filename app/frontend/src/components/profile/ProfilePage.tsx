import { useState } from 'react';
import type { ReportStatus } from '../../types/Report';
import { useUserInfo } from '../../hooks/useUserInfo';
import { useMyReportedFires } from '../../hooks/useMyReportedFires';
import { MyFireReportsTable } from '../../components/profile/FireReportsTable';
import { ReportFilterTabs } from '../../components/admin/reportFilter';
import { SearchBar } from '../../components/admin/searchBar';

export default function ProfilePage(){
    const { user, isLoading} = useUserInfo();
    const { reports, loading: reportsLoading, error: reportsError } = useMyReportedFires();
    const [filter, setFilter] = useState<'All' | ReportStatus>('All');
    const [search, setSearch] = useState('');

    let name = "";
    let initial = "";
    if (user) {
        name = `${user.name} ${user.surname}`;
        initial = user.name.charAt(0);
    } else if (isLoading) {
        name = "Loading...";
        initial = "?";
    } else {
        name = "Not signed in";
        initial = "?";
    }

    const filteredReports = reports.filter(
        (report) =>
            report.location_text.toLowerCase().includes(search.toLowerCase()) ||
            report.id.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className='p-6'>
            <div className='flex items-center gap-8 mt-6 mb-8 pb-8 bg-card'>
                <div className='w-20 h-20 rounded-full bg-ignite flex items-center justify-center text-4xl font-display font-bold text-char shrink-0'>{initial}</div>
                <div className="min-w-0">
                    <h1 className="text-text-primary uppercase">{name}</h1>
                    {user ? (
                        <h4 className="text-text-muted mt-0.5 uppercase">{user.role}</h4>
                    ) : null}
                </div>
            </div>
            {user ? (
                <div className='w-full rounded-2xl border border-carbon-stroke p-4 flex flex-col'>
                    <h2 className='uppercase mb-3'>
                        My Fire Reports
                    </h2>

                    <div className='flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-3'>
                        <SearchBar value={search} onChange={setSearch} placeholder='Search...' />
                        <ReportFilterTabs filter={filter} onChange={setFilter} />
                    </div>
        
                    {reportsError && <div>{reportsError}</div>}
 
                    {reportsLoading ? (
                    <div className="flex justify-center items-center min-h-[20vh]">
                        <span className="loading loading-spinner loading-lg text-primary" />
                    </div>
                    ) : (
                        <MyFireReportsTable reports={filteredReports} filter={filter} />
                    )}
                </div>
            ) : null}
        </div>
    );
}
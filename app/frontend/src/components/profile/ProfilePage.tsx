import { useState } from 'react';
import type { ReportStatus } from '../../types/Report';
import type { Status } from '../../types/Resource';
import type { UserResponse } from '../../types/User';
import { useUserInfo } from '../../hooks/useUserInfo';
import { useMyReportedFires } from '../../hooks/useMyReportedFires';
import { useMyResources, useMyResource } from '../../hooks/useMyResource';
import { useUpdateResourceStatus } from '../../hooks/useUpdateResourceStatus';
import { MyFireReportsTable } from './FireReportsTable';
import { MyResourcesTable } from './ResourcesTable';
import { StatusFilter } from '../../components/shared/Filter';
import { SearchBar } from '../../components/shared/Searchbar';
import { Info } from './Info';

type ReportFilter = 'All' | ReportStatus;
type ResourceFilter = 'All' | Status;

const REPORT_FILTERS: readonly ReportFilter[] = ['All', 'pending', 'received', 'rejected', 'verified'];
const RESOURCE_FILTERS: readonly ResourceFilter[] = ['All', 'available', 'dispatched', 'unavailable'];

export default function ProfilePage(){
    const { user, isLoading} = useUserInfo();
    const { reports, loading: reportsLoading, error: reportsError } = useMyReportedFires();
    const { resources, loading: resourcesLoading, error: resourcesError, refetch } = useMyResources();
    const [filter, setFilter] = useState<ReportFilter>('All');
    const [search, setSearch] = useState('');
    const [resourceFilter, setResourceFilter] = useState<ResourceFilter>('All');
    const [resourceSearch, setResourceSearch] = useState('');
    const { updateStatus } = useUpdateResourceStatus();
    const [updatedUser, setUpdatedUser] = useState<UserResponse | null>(null);

    const displayUser = updatedUser ?? user;

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

     const filteredResources = resources.filter(
        (resource) =>
            resource.location.toLowerCase().includes(search.toLowerCase()) ||
            resource.id.toLowerCase().includes(search.toLowerCase())
    );

    async function handleStatusChange(id: string, status: Status) {
        await updateStatus(id, status); 
        refetch();
    }

    return (
        <div className='p-6'>
            <div className='flex items-center gap-8 mt-6 mb-8 pb-8 bg-card'>
                <div className='w-20 h-20 rounded-full bg-ignite flex items-center justify-center text-4xl font-display font-bold text-char shrink-0'>{initial}</div>
                <div className="min-w-0">
                    <h1 className="text-text-primary uppercase">{name}</h1>
                    {displayUser ? (
                        <h4 className="text-text-muted mt-0.5 uppercase">{displayUser.role}</h4>
                    ) : null}
                </div>
            </div>
            {displayUser ? (
                <div className='mb-6'>
                    <Info user={displayUser} onUpdated={setUpdatedUser} />
                </div>
            ): null}
            {user ? (
                <div className='w-full rounded-2xl border border-carbon-stroke p-4 flex flex-col'>
                    <h2 className='uppercase mb-3'>
                        My Fire Reports
                    </h2>

                    <div className='flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-3'>
                        <SearchBar value={search} onChange={setSearch} placeholder='Search...' />
                        <StatusFilter<ReportFilter> options={REPORT_FILTERS} filter={filter} onChange={setFilter} />
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

            {user ? (
                <div className='w-full rounded-2xl border border-carbon-stroke p-4 flex flex-col'>
                    <h2 className='uppercase mb-3'>
                        My Resources
                    </h2>

                    <div className='flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-3'>
                        <SearchBar value={resourceSearch} onChange={setResourceSearch} placeholder='Search...' />
                        <StatusFilter<ResourceFilter> options={RESOURCE_FILTERS} filter={resourceFilter} onChange={setResourceFilter} />
                    </div>
        
                    {resourcesError && <div>{resourcesError}</div>}
 
                    {resourcesLoading ? (
                    <div className="flex justify-center items-center min-h-[20vh]">
                        <span className="loading loading-spinner loading-lg text-primary" />
                    </div>
                    ) : (
                        <MyResourcesTable resources={filteredResources} filter={resourceFilter} onStatusChange={handleStatusChange} />
                    )}
                </div>
            ) : null}
        </div>
    );
}
import React, { useState } from 'react';
import { ReportStatus } from '../../types/Report';
import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import { ReportsTable } from '../../components/firefighter/reportsTable';
import { StatusTableFilter } from '../../components/firefighter/reportsFilter';
import { TableSearchBar } from '../../components/firefighter/searchbar';
import { useFirefighterReports } from '../../hooks/useFirefighterReports';
import { PageHeader } from '../../components/layout/pageHeader';

export default function ReportTable() {
  const [statusFilter, setStatusFilter] = useState<'all' | ReportStatus>('all');
  const [searchKey, setSearchKey] = useState('');
  const { reports, loading, error } = useFirefighterReports(searchKey);

  return (
    <FirefighterSideBar>
      <div className="p-4 flex flex-col h-full w-full gap-y-3">
        <PageHeader title="Reported Fires" subtitle="View the reported fires" showIcons />
        {/* Header + filter + search */}
        <div className="flex justify-between items-center">
          <StatusTableFilter filter={statusFilter} onChange={setStatusFilter} />

          <TableSearchBar value={searchKey} onChange={setSearchKey} />
        </div>

        {error && <div className="text-error text-sm">{error}</div>}

        {loading ? (
          <div className="flex justify-center items-center min-h-[40vh]">
            <span className="loading loading-spinner loading-lg text-primary" />
          </div>
        ) : (
          <ReportsTable
            requests={reports}
            filter={statusFilter}
            onView={(req) => console.log(req)}
          />
        )}
      </div>
    </FirefighterSideBar>
  );
}

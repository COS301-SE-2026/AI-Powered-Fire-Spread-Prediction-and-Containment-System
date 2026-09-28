import React, { useState } from 'react';
import { RotateHint } from '@/components/shared/RotateHint';
import { ReportStatus } from '../../types/Report';
import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import { ReportsTable } from '../../components/firefighter/reportsTable';
import { StatusFilter } from '../../components/shared/Filter';
import { SearchBar } from '../../components/shared/Searchbar';
import { useFirefighterReports } from '../../hooks/useFirefighterReports';
import { useRotate } from '../../hooks/useRotate'
import { PageHeader } from '../../components/layout/pageHeader';

  type ReportFilter = 'all' | ReportStatus;
  const REPORT_FILTERS: readonly ReportFilter[] = ['all', 'pending', 'verified', 'rejected'];

export default function ReportTable() {
  const [statusFilter, setStatusFilter] = useState<ReportFilter>('all');
  const [searchKey, setSearchKey] = useState('');
  const { reports, loading, error } = useFirefighterReports(searchKey);
  const { showHint, dismiss } = useRotate();

  return (
    <FirefighterSideBar hideLoginRegister>
      <div className="p-2 flex flex-col w-full gap-y-3">
        <RotateHint show={showHint} onDismiss={dismiss} />
        <PageHeader title="Reported Fires" subtitle="View the reported fires" showIcons />
        {/* Header + filter + search */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-2 md-4">
          <SearchBar value={searchKey} placeholder="Search reported fires" onChange={setSearchKey} />
          <StatusFilter<ReportFilter> options={REPORT_FILTERS} filter={statusFilter} onChange={setStatusFilter} />
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

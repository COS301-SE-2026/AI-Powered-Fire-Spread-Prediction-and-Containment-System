import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';
import { ChevronLeft } from 'lucide-react';
import { ReportDetails } from './reportDetails';
import { ReportDescription } from './reportDescription';
import { ReportActions } from './reportActions';
import { ReportPhoto } from './reportPhoto';
import { useFireReport } from '../../hooks/useFireReport';
import { PageHeader } from '../layout/pageHeader';

const ReportMap = dynamic(() => import('./reportMapCard').then((mod) => mod.ReportMap), {
  ssr: false,
});

interface ViewProps {
  reportRef: string;
  role?: 'admin' | 'firefighter';
}

export function ViewPage({ reportRef, role = 'admin' }: Readonly<ViewProps>) {
  const router = useRouter();
  const { report, loading, error, refetch } = useFireReport(reportRef);

  if (loading)
    return (
      <div className="p-6">
        <p className="text-text-muted">Loading report...</p>
      </div>
    );

  if (error || !report)
    return (
      <div className="p-6">
        <p className="text-error">{error ?? 'Report not found.'}</p>
      </div>
    );

    return (
        <div className="p-2 flex flex-col h-full w-full">

            <button type="button" onClick={() => router.back()} aria-label="Back" className="btn btn-sm btn-outline btn-square rounded-lg shrink-0"><ChevronLeft className='w-4 h-4' /></button>
            <PageHeader title={`Report ${report.reference_number}`} subtitle="Viewing fire report details" showIcons />



            {/* 2 cols */}
            <div className='grid grid-cols-1 lg:grid-cols-12 gap-2 h-full'>
                {/* left */}
                <div className='lg:col-span-6 flex flex-col gap-3'>
                    <div className="relative overflow-hidden flex-1 w-full">
                        <ReportMap lat={report.lat} lng={report.lng} />
                    </div>
                    <ReportDetails report={report} />
                </div>
                {/* right */}
                <div className='lg:col-span-6 flex flex-col gap-2 h-full'>
                    <ReportPhoto report={report} />
                    <ReportDescription report={report} />
                    <ReportActions reportRef={report.reference_number} status={report.status} onStatusChange={refetch} />
                </div>
            </div>
        </div>
    );
}

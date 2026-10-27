import { SECTIONS } from '@/lib/skeletonRoutes';
import { AdminDashboardSkeleton } from './AdminDashboardSkeleton';
import { AdminLiveMapSkeleton } from './AdminLiveMapSkeleton';
import { DashboardSkeleton } from './DashboardSkeleton';
import { FirefighterDashboardSkeleton } from './FirefighterDashboardSkeleton';
import { GuestLiveMapSkeleton } from './GuestLiveMapSkeleton';
import { HelpPageSkeleton } from './HelpPageSkeleton';
import { ProfilePageSkeleton } from './ProfilePageSkeleton';
import { PublicPageSkeleton } from './PublicPageSkeleton';
import { RegisterPageSkeleton } from './RegisterPageSkeleton';
import { ReportDetailSkeleton } from './ReportDetailSkeleton';
import { ReportPageSkeleton } from './ReportPageSkeleton';
import { SimulationPageSkeleton } from './SimulationPageSkeleton';
import { UserLiveMapSkeleton } from './UserLiveMapSkeleton';
import { TablePageSkeleton } from './TablePageSkeleton'


export function RouteSkeleton({ url }: Readonly<{ url: string }>) {
    const path = url.split('?')[0].split('#')[0].toLowerCase();
    const parts = path.split('/').filter(Boolean);
    const section = parts[0] ?? '';
    const page = parts[parts.length - 1] ?? '';

    if (!SECTIONS.includes(section)) {
        return page === 'register' ? <RegisterPageSkeleton /> : <PublicPageSkeleton />;
    }

    const tablePages = ['reported-fire', 'reported-fires', 'approvals', 'gpuworkers', 'gpuvolunteer'];
    const reportPages = ['report-fire', 'registerresource'];

    if (page === 'dashboard') {
        return section === 'admin' ? <AdminDashboardSkeleton /> : <FirefighterDashboardSkeleton />;
    }
    
    if (page === 'live-map'){
        if (section === 'users') return <UserLiveMapSkeleton />;
        if (section === 'guests') return <GuestLiveMapSkeleton />;
        return <AdminLiveMapSkeleton />
    }

    if (page === 'simulation') return <SimulationPageSkeleton />;
    if (tablePages.includes(page)) return <TablePageSkeleton />;
    if (reportPages.includes(page)) return <ReportDetailSkeleton />;
    if (page === 'profile') return <ProfilePageSkeleton />;
    if (page === 'help') return <HelpPageSkeleton />;

    return <ReportDetailSkeleton />;
}
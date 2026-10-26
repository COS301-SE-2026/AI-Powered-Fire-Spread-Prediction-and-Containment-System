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

    switch (page) {
        case 'dashboard':
            return section === 'admin' ? <AdminDashboardSkeleton /> : <FirefighterDashboardSkeleton />;
        case 'live-map':
            if (section === 'users') return <UserLiveMapSkeleton />;
            if (section === 'guests') return <GuestLiveMapSkeleton />;
        case 'simulation':
            return <SimulationPageSkeleton />;
        case 'reported-fire':
        case 'reported-fires':
        case 'approvals':
        case 'gpuworkers':
        case 'gpuvolunteer':
            return <TablePageSkeleton />;
        case 'report-fire':
        case 'registerresource':
            return <ReportPageSkeleton />;
        case 'profile':
            return <ProfilePageSkeleton />;
        case 'help':
            return <HelpPageSkeleton />;
        default:
            return <ReportDetailSkeleton />
    }
}
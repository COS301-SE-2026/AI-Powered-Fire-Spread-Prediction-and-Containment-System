import { SECTIONS } from "@/lib/skeletonRoutes";
import { TablePageSkeleton } from "./TablePageSkeleton";
import { DashboardSkeleton } from "./DashboardSkeleton";
import { MapPageSkeleton } from "./MapPageSkeleton";
import { ProfilePageSkeleton } from "./ProfilePageSkeleton";
import { FormPageSkeleton } from "./FormPageSkeleton";
import { DetailPageSkeleton } from "./DetailPageSkeleton";
import { PublicPageSkeleton } from "./PublicPageSkeleton";

export function RouteSkeleton({ url }: Readonly<{ url: string }>) {
    const path = url.split('?')[0].split('#')[0].toLowerCase();
    const parts = path.split('/').filter(Boolean);
    const section = parts[0] ?? '';
    const page = parts[parts.length - 1] ?? '';

    if (!SECTIONS.includes(section)) return <PublicPageSkeleton />;

    if (page === 'dashboard') {
        return section === 'admin' ? <DashboardSkeleton /> : <MapPageSkeleton />;
    }

    if (page === 'analytics') return <DashboardSkeleton label='Loading analytics' />
    if (['live-map', 'simulation'].includes(page)) return <MapPageSkeleton />;
    if (['reported-fire', 'reported-fires', 'approvals', 'gpuworkers', 'gpuvolunteer'].includes(page)) {
        return <TablePageSkeleton />;
    }

    if (page === 'profile') return <ProfilePageSkeleton />;
    if (['report-fire', 'registerresource'].includes(page)) return <FormPageSkeleton />;
    return <DetailPageSkeleton />
}
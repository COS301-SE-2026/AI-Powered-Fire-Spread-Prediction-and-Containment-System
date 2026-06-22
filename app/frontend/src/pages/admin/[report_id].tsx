import { useRouter } from 'next/router';
import { SideBarLayout } from '../../components/demoSidebar';

export default function ReportedFiresViewPage() {
    const router = useRouter();
    const { report_id } = router.query;

    return (
        <SideBarLayout>
            <div className="p-6">
                <h1 className="uppercase">Fire Report — {report_id}</h1>
                <p className="text-text-muted">Details coming soon.</p>
            </div>
        </SideBarLayout>
    );
}
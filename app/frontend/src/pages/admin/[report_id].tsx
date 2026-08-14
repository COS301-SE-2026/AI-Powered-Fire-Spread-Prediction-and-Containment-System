import { useRouter } from 'next/router';
import { AdminSideBar } from '../../components/admin/AdminSideBar'; 
import { ViewPage } from '../../components/admin/ReportView';

export default function View() {
    const router = useRouter();
    const { report_id } = router.query;
    if (!report_id) return null;

    return (
        <AdminSideBar>
            <ViewPage report_ref = {report_id as string}/>
        </AdminSideBar>
    );
}
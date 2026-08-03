import { useRouter } from 'next/router';
import { FirefighterSideBar } from '../../components/firefighter/firefighterSidebar'; 
import { ViewPage } from '../../components/admin/ReportView';

export default function View() {
    const router = useRouter();
    const { ['report-ref']: reportRef } = router.query;
    if (!reportRef) return null;

    return (
        <FirefighterSideBar>
            <ViewPage report_ref = {reportRef as string}/>
        </FirefighterSideBar>
    );
}
import { useRouter } from 'next/router';
import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import { ViewPage } from '../../components/admin/ReportView';

export default function View() {
  const router = useRouter();
  const { 'report-ref': reportRef } = router.query;
  if (!reportRef) return null;

  return (
    <FirefighterSideBar>
      <ViewPage reportRef={reportRef as string} />
    </FirefighterSideBar>
  );
}

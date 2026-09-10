import { useRouter } from 'next/router';
import { AdminSideBar } from '../../components/admin/AdminSideBar';
import { ViewPage } from '../../components/admin/ReportView';

export default function View() {
  const router = useRouter();
  const { report_id: reportId } = router.query;
  if (!router.isReady || !reportId) return null;

  return (
    <AdminSideBar hideLoginRegister>
      <ViewPage reportRef={reportId as string} />
    </AdminSideBar>
  );
}

import { useRouter } from 'next/router';
import { UserSideBar } from '../../components/users/UserSideBar';
import { ViewPage } from '../../components/admin/ReportView';

export default function View() {
  const router = useRouter();
  const { report_id: reportId } = router.query;
  if (!router.isReady || !reportId) return null;

  return (
    <UserSideBar hideLoginRegister>
      <ViewPage reportRef={reportId as string} role="user" />
    </UserSideBar>
  );
}

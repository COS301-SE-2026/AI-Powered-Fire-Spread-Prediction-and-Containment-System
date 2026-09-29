import { useRouter } from 'next/router';
import { UserSideBar } from '../../components/users/UserSideBar';
import { ViewPage } from '../../components/admin/ReportView';

export default function View() {
  const router = useRouter();
  const { report_id: reportId } = router.query;
  if (!router.isReady || !reportId) return null;

  return (
    <UserSideBar hideLoginRegister>
      {/* eslint-disable-next-line jsx-a11y/aria-role -- "role" here is ViewPage's own domain prop (admin/user), not an ARIA role */}
      <ViewPage reportRef={reportId as string} role="user" />
    </UserSideBar>
  );
}

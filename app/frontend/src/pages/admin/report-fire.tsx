import { AdminSideBar } from '../../components/admin/AdminSideBar';
import ReportPage from '../../components/reportfire/ReportPage';

export default function AdminReportFire() {
  return (
    <AdminSideBar hideLoginRegister>
      <ReportPage />
    </AdminSideBar>
  );
}

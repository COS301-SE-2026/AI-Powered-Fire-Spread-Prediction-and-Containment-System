import { AdminSideBar } from '../../components/admin/AdminSideBar';
import RegisterResource from '../../components/resources/RegisterResourcePage';

export default function RegisteredReportFire() {
  return (
    <AdminSideBar hideLoginRegister>
      <RegisterResource />
    </AdminSideBar>
  );
}

import { AdminSideBar } from '../../components/admin/AdminSideBar';
import SimulationPage  from '../../components/firefighter/SimulationPage';

export default function AdminSimulationPage() {
  return (
    <AdminSideBar hideLoginRegister>
      <SimulationPage />
    </AdminSideBar>
  );
}

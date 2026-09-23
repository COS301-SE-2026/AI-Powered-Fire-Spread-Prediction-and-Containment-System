import { AdminSideBar } from '../../components/admin/AdminSideBar';
import GPUWorkersPage  from '../../components/gpu_worker/GPUWorkersPage';

export default function GpuWorkers() {
  return (
    <AdminSideBar hideLoginRegister>
      <GPUWorkersPage />
    </AdminSideBar>
  );
}

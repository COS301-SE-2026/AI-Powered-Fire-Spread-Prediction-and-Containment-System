import { AdminSideBar } from '../../components/admin/AdminSideBar';
import GPUWorkersPage  from '../../components/gpu_worker/GpuWorkersPage';

export default function GpuWorkers() {
  return (
    <AdminSideBar hideLoginRegister>
      <GPUWorkersPage />
    </AdminSideBar>
  );
}

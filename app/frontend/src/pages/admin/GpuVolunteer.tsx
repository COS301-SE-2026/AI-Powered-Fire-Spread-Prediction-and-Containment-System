import { AdminSideBar } from '../../components/admin/AdminSideBar';
import GPUVolunteerPage  from '../../components/gpu_worker/VolunteerPage';

export default function GpuWorkers() {
  return (
    <AdminSideBar hideLoginRegister>
      <GPUVolunteerPage />
    </AdminSideBar>
  );
}

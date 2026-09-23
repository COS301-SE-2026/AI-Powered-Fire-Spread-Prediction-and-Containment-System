import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import GPUWorkersPage  from '../../components/gpu_worker/GPUWorkersPage';

export default function GpuWorkers() {
  return (
    <FirefighterSideBar hideLoginRegister>
      <GPUWorkersPage />
    </FirefighterSideBar>
  );
}

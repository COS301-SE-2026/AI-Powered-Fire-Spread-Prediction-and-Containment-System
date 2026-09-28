import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import VolunteerPage  from '../../components/gpu_worker/VolunteerPage';

export default function GpuWorkers() {
  return (
    <FirefighterSideBar hideLoginRegister>
      <VolunteerPage />
    </FirefighterSideBar>
  );
}

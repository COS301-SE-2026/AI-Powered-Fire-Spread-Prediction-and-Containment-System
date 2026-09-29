import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import SimulationPage from '../../components/firefighter/SimulationPage';

export default function FirefighterSimulationPage() {
  return (
    <FirefighterSideBar hideLoginRegister>
      <SimulationPage />
    </FirefighterSideBar>
  );
}

import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import RegisterResource from '../../components/resources/RegisterResourcePage';

export default function RegisteredReportFire() {
  return (
    <FirefighterSideBar hideLoginRegister>
      <RegisterResource />
    </FirefighterSideBar>
  );
}

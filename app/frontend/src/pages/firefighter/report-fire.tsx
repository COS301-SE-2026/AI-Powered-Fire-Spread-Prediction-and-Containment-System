import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import ReportPage from '../../components/reportfire/ReportPage';

export default function FirefighterReportFire() {
  return (
    <FirefighterSideBar hideLoginRegister>
      <ReportPage />
    </FirefighterSideBar>
  );
}

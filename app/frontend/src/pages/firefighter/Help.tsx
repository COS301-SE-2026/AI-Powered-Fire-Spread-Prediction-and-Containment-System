import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import HelpPage from '../../components/shared/HelpPage';

export default function FirefighterHelpPage() {
    return (
        <FirefighterSideBar hideLoginRegister>
            <HelpPage />
        </FirefighterSideBar>
    )
}
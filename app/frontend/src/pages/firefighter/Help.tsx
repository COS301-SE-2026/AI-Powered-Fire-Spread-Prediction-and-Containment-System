import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import HelpPage from '../../components/shared/HelpMenu';

export default function FirefighterHelpPage() {
    return (
        <FirefighterSideBar hideLoginRegister>
            <HelpPage />
        </FirefighterSideBar>
    )
}
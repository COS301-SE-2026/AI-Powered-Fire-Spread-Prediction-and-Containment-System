import { FirefighterSideBar } from '../../components/firefighter/FirefighterSidebar';
import ProfilePage from '../../components/profile/ProfilePage';

export default function FirefighterProfilePage() {
    return (
        <FirefighterSideBar hideLoginRegister>
            <ProfilePage />
        </FirefighterSideBar>
    )
}
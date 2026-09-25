import { UserSideBar } from '../../components/users/UserSideBar';
import ProfilePage from '../../components/profile/ProfilePage';

export default function UserProfilePage() {
    return (
        <UserSideBar>
            <ProfilePage />
        </UserSideBar>
    )
}
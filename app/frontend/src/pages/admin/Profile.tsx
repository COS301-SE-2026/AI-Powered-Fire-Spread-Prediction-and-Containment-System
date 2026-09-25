import { AdminSideBar } from '@/components/admin/AdminSideBar';
import ProfilePage from '../../components/profile/ProfilePage';

export default function AdminProfilePage() {
    return (
        <AdminSideBar hideLoginRegister>
            <ProfilePage />
        </AdminSideBar>
    )
}
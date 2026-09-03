import { AdminSideBar } from '@/components/admin/AdminSideBar';
import HelpPage from '../../components/shared/HelpMenu';

export default function AdminHelpPage() {
    return (
        <AdminSideBar hideLoginRegister>
            <HelpPage />
        </AdminSideBar>
    )
}
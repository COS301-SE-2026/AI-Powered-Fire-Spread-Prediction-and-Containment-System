import { AdminSideBar } from '../../components/admin/adminSidebar';
import MapView from '../../components/guest/guestLanding';

export default function AdminLiveMap() {
    return (
        <AdminSideBar>
            <MapView/>
        </AdminSideBar>
    );
}

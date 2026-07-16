import React from 'react';
import { Map, LayoutDashboard, BookAlert } from 'lucide-react';
import { SideBar, NavLink } from '../Sidebar';

export function FirefighterItems() {
    return (
        <>
            <NavLink icon={LayoutDashboard} label="Firefighter Dashboard" href="/firefighter/firefighter-dashboard" />
            <NavLink icon={BookAlert} label="Reported Fires" href="/admin/analytics" />
            <NavLink icon={Map} label="Fire Simulation AI" href="/admin/adminLiveMap" />
        </>
    );
}

export function FirefighterSideBar({
    children,
    hideLogout = false,
    hideLoginRegister = false,
}: Readonly<{
    children?: React.ReactNode;
    hideLogout?: boolean;
    hideLoginRegister?: boolean;
}>) {
    return(
        <SideBar items={<FirefighterItems/>} hideLogout={hideLogout} hideLoginRegister={hideLoginRegister}>{children}</SideBar>
    );
}

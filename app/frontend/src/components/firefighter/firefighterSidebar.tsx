import React from 'react';
import { Map, Flame, LayoutDashboard, BookAlert } from 'lucide-react';
import { SideBar, NavLink } from '../Sidebar';

export function FirefighterItems() {
    return (
        <>
            <NavLink icon={LayoutDashboard} label="Firefighter Dashboard" href="/firefighter/dashboard" />
            <NavLink icon={BookAlert} label="Reported Fires" href="/firefighter/reported-fires" />
            <NavLink icon={Flame} label="Report a Fire" href="/firefighter/report-fire" />
            <NavLink icon={Map} label="Fire Simulation AI" href="/firefighter/simulation" />
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

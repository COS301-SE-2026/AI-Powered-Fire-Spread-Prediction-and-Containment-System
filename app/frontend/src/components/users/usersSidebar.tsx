import React from 'react';
import { Map, Flame, House, MessageCircleWarning, MessagesSquare} from 'lucide-react';
import { SideBar, NavLink } from '../Sidebar';

export function UserItems() {
    return (
        <>
            <NavLink icon={House} label="Home" href="/user/live-map" />
            <NavLink icon={Flame} label="Report a Fire" href="../user/report-fire"/>
            <NavLink icon={Map} label="Fire Simulation" href="/user/simulation"/>
            <NavLink icon={MessageCircleWarning} label="Notifications" href="/user/under-construction" />
            <NavLink icon={MessagesSquare} label="Community" href="/user/under-construction" />
        </>
    );
}

export function UserSideBar({
    children,
    hideLogout = false,
    hideLoginRegister = false,
}: Readonly<{
    children?: React.ReactNode;
    hideLogout?: boolean;
    hideLoginRegister?: boolean;
}>) {
    return(
        <SideBar items={<UserItems/>} hideLogout={hideLogout} hideLoginRegister={hideLoginRegister}>{children}</SideBar>
    );
}

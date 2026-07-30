import React from 'react';
import { Map, Flame, House, MessageCircleWarning, MessagesSquare} from 'lucide-react';
import { SideBar, NavLink } from '../Sidebar';

export function UserItems() {
    return (
        <>
            <NavLink icon={House} label="Home" href="/registeredUser/registeredUserLanding" />
            <NavLink icon={Flame} label="Report a Fire" href="../registeredUser/registeredReportFire" />
            <NavLink icon={Map} label="Fire Simulation" href="/registeredUser/registeredUnderConstruction" />
            <NavLink icon={MessageCircleWarning} label="Notifications" href="/registeredUser/registeredUnderConstruction" />
            <NavLink icon={MessagesSquare} label="Community" href="/registeredUser/registeredUnderConstruction" />
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

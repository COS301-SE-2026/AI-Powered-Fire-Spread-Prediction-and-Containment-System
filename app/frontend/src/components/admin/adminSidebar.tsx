import React from 'react';
import { Map, LayoutDashboard, ShieldAlert, Flame, TrendingUp, PlusCircle } from 'lucide-react';
import { SideBar, NavLink } from '../Sidebar';

export function AdminItems() {
    return (
        <>
            <NavLink icon={LayoutDashboard} label="Admin Dashboard" href="/admin/adminDashboard" />
            <NavLink icon={TrendingUp} label="Analytics" href="/admin/analytics" />
            <NavLink icon={Map} label="Live Map" href="/admin/adminLiveMap" />
            <NavLink icon={PlusCircle} label="Report a Fire" href="/admin/adminReportFire" />
            <NavLink icon={ShieldAlert} label="Role Approvals" href="/admin/approvalPage" />
            <NavLink icon={Flame} label="Reported Fires" href="/admin/reportedfiresPage" />
        </>
    );
}

export function AdminSideBar({
    children,
    hideLogout = false,
    hideLoginRegister = false,
}: Readonly<{
    children?: React.ReactNode;
    hideLogout?: boolean;
    hideLoginRegister?: boolean;
}>) {
    return(
        <SideBar items={<AdminItems/>} hideLogout={hideLogout} hideLoginRegister={hideLoginRegister}>{children}</SideBar>
    );
}

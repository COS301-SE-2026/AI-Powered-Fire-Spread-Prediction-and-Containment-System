import {Map, CircleAlert} from 'lucide-react'
import { SideBar, NavLink } from "../../components/layout/Sidebar";
import ReportPage from "../../components/reportfire/report";

export default function RegisteredReportFire(){
    const guestNavItems =(
            <>
                <NavLink icon={Map} label="Live Map" href="/guests/live-map"/>
                <NavLink icon={CircleAlert} label="Report Fire" href="/guests/report-fire"/>
            </>
          );
    return(<SideBar items={guestNavItems}>
        <ReportPage/>
    </SideBar>);
    }
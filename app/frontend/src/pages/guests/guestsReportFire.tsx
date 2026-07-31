import { SideBar, NavLink } from "../../components/Sidebar";
import {Map, CircleAlert} from 'lucide-react'
import ReportPage from "../../components/reportfire/report";

export default function RegisteredReportFire(){
    const guestNavItems =(
            <>
                <NavLink icon={Map} label="Live Map" href="/guests/guestsLanding"/>
                <NavLink icon={CircleAlert} label="Report Fire" href="/guests/guestsReportFire"/>
            </>
          );
    return(<SideBar items={guestNavItems}>
        <ReportPage/>
    </SideBar>);
    }
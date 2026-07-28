import React, { useEffect, useState } from 'react';
import { BookAlert, Map, LayoutDashboard, ShieldAlert, Flame, User, UserCircle, ChevronDown, PlusCircle} from 'lucide-react';
import { SideBar, NavLink } from './Sidebar';
import { AdminItems } from './admin/adminSidebar';

const SideBarDropdown = ({ title, icon: Icon, defaultOpen = false, isSidebarHovered, children }: { 
    title: string; 
    icon: React.ElementType;
    defaultOpen?: boolean;
    isSidebarHovered: boolean;
    children: React.ReactNode;
}) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    useEffect(() => {
        if(!isSidebarHovered){
            setIsOpen(false);
        }
    }, [isSidebarHovered])

    return(
        <li className="w-full flex flex-col">
            <button onClick={() => setIsOpen(!isOpen)} className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active-scale[0.98] transition-all w-full text-left">
                <Icon className={`size-6 shrink-0 transition-colors ${isOpen ? 'text-ignite' : 'text-neutral/70 group-hover:text-ignite'}`} />

                <span className="test-sm font-semibold tracking-wide text-neutral flex-1 hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                    {title}
                </span>

                <ChevronDown className={`size-4 text-neutral/50 hidden group-hover:block transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}/>
            </button>

            {/* dropdown content */}
            <div className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? 'max-h-96 opacity-100 ml-1' : 'max-h-0 opacity-0'}`}>
                <div className="flex flex-col space-y-1 w-full">
                    {children}
                </div>
            </div>
        </li>
    );
};

export function SideBarLayout({
    children,
    hideLogout = false,
    hideLoginRegister = false,
}: {
    children?: React.ReactNode;
    hideLogout?: boolean;
    hideLoginRegister?: boolean;
}) {

    const [isHovered, setIsHovered] = useState(false);

    return(
        <div onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)}>
            <SideBar hideLogout={hideLogout} hideLoginRegister={hideLoginRegister} 
                items={
                    <>
                        {/* admin dropdown */}
                        <SideBarDropdown title="Admin Portal" icon={ShieldAlert} isSidebarHovered={isHovered}>
                            <AdminItems />
                        </SideBarDropdown >

                        {/* firefighter dropdown */}
                        <SideBarDropdown  title="Firefighter Tools" icon={Flame} defaultOpen={true} isSidebarHovered={isHovered}>
                            <NavLink icon={LayoutDashboard} label="Firefigther Dashboard" href="/firefighterDashboard" />
                            <NavLink icon={BookAlert} label="Reported Fires" />
                            <NavLink icon={Map} label="Fire Simulation AI" />
                        </SideBarDropdown >

                        {/* registered user dropdown */}
                        <SideBarDropdown  title="Registered User" icon={User} isSidebarHovered={isHovered}>
                            <NavLink icon={Map} label="Live Map (User View)" href="/registeredUser/registeredUserLanding" />
                            <NavLink icon={PlusCircle} label="Report a Fire" href="/registeredUser/ReportFire" />
                        </SideBarDropdown >

                        {/* guest dropdown */}
                        <SideBarDropdown  title="Guest Access" icon={UserCircle} isSidebarHovered={isHovered}>
                            <NavLink icon={Map} label="Public Fire Map" href="/guests/guestsLanding" />
                            <NavLink icon={PlusCircle} label="Submit Report" href="/registeredUser/ReportFire" />
                        </SideBarDropdown >
                    </>
                }
            >
                {children}
            </SideBar>
        </div>
    );
}
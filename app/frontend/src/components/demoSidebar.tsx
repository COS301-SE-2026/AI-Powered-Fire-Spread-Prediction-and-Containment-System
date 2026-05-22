import React, { Children, useEffect, useState } from 'react';
import Link from 'next/link';
import { BookAlert, Map, LayoutDashboard, Settings, LogOut,
    ShieldAlert, Flame, User, UserCircle,
    ChevronDown, TrendingUp, PlusCircle
} from 'lucide-react';

const NavLink = ({ icon: Icon, label, href }: { icon: any; label: string; href?: string }) => {
    const content = (
        <>
            <Icon className="size-5 shrink-0 ml-1 group-hover:ml-6 transition-all" />
            <span className="text-sm font-medium tracking-wide hidden group-hover:inline opacity-0 group-hover:opacity-100 tranistion-opacity duration-200 whitespace-nowrap">
                {label}
            </span>
        </>
    );

    const className =
        "py-2.5 px=4 w-full rounded-lg flex items-center justify-center group-hover:justify-start gap-4 hover:bg-smoke-hover active:scale-[0.98] transition-all text-left text-neutral/80 hoverLtext-neutral";

    return href ? (
        <Link href={href} className={className}>
            {content}
        </Link>
    ) : (
        <button className={className}>
            {content}
        </button>
    );
};

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
        <div className="flex min-h-screen bg-carbon-bg text-neutral font-body antialised realtive z-0">
            {/* Atmospheric Background Blooms */}
            <div className="global-atmos">
                <div className="ga-bloom-primary"></div>
                <div className="ga-bloom-secondary"></div>
            </div>

            <aside onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)} className="hidden lg:flex flex-col items-center bg-carbon-side border-r border-carbon-card h-screen sticky top-0 z-40 transition-all duration-300 ease-in-out group w-[92px] hover:w-64 shrink-0 shadow-2xl shadow-black/50">

            {/* Logo Area */}
            <div className="flex items-center justify-center group-hover:justify-start group-hover:px-6 mt-6 mb-4 px-2 shrink-0 transition-all duration-300 w-full">
                <img src="/images/logo-small.png" alt="FireAway" className="h-12 w-10 object-contain group-hover:hidden"/>
                <img src="/images/logo-large.png" alt="FireAway" className="h-20 w-48 object-contain hidden group-hover:block"/>
            </div>

            {/* Main Navigation */}
                <div className="w-full grow overflow-y-auto overflow-x-hidden scrollbar-hide">
                    <ul className="menu w-full px-3 space-y-2 flex flex-col items-center group-hover:items-start">
                        
                        {/* Admin Dropdown */}
                        <SideBarDropdown title="Admin Portal" icon={ShieldAlert} isSidebarHovered={isHovered}>
                            <NavLink icon={LayoutDashboard} label="Admin Dashboard" />
                            <NavLink icon={TrendingUp} label="Analytics" />
                            <NavLink icon={Map} label="Live Map" href="/guests" />
                            <NavLink icon={ShieldAlert} label="Role Approvals" href="/admin/approvalPage" />
                            <NavLink icon={Flame} label="Reported Fires" />
                        </SideBarDropdown >

                        {/* Firefighter Dropdown */}
                        <SideBarDropdown  title="Firefighter Tools" icon={Flame} defaultOpen={true} isSidebarHovered={isHovered}>
                            <NavLink icon={LayoutDashboard} label="Firefigther Dashboard" href="/firefighterDashboard" />
                            <NavLink icon={BookAlert} label="Reported Fires" />
                            <NavLink icon={Map} label="Fire Simulation AI" />
                        </SideBarDropdown >

                        {/* Registered User Dropdown */}
                        <SideBarDropdown  title="Registered User" icon={User} isSidebarHovered={isHovered}>
                            <NavLink icon={Map} label="Live Map (User View)" />
                            <NavLink icon={PlusCircle} label="Report a Fire" href="/reportfire" />
                        </SideBarDropdown >

                        {/* Guest Dropdown */}
                        <SideBarDropdown  title="Guest Access" icon={UserCircle} isSidebarHovered={isHovered}>
                            <NavLink icon={Map} label="Public Fire Map" href="/guests" />
                            <NavLink icon={PlusCircle} label="Submit Report" href="/reportfire" />
                        </SideBarDropdown >
                    </ul>

                    {/* Settings Section */}
                    <div className="w-full border-t border-carbon-card bg-carbon-side shrink-0 flex flex-col px-3 py-4 gap-2">
                        <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase block text-center group-hover:hidden">SYS</span>
                        <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase hidden group-hover:block text-left px-2">SYSTEM SETTINGS</span>
                    </div>

                    {!hideLogout && (
  <button className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left">
    <Settings className="size-6 text-neutral/70 group-hover:text-ignite shrink-0 transition-colors" />
    <span className="text-sm font-semibold hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
      Global Settings
    </span>
  </button>
)}

                </div>

                 {/* Footer Action */}
                <div className="w-full p-4 border-t border-carbon-card flex flex-col items-center gap-2 group-hover:items-start group-hover:px-6 transition-all bg-carbon-side shrink-0">
                    {!hideLoginRegister && (
                        <Link href="/" className="p-2 text-neutral hover:text-white rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center group-hover:justify-start gap-4">
                            <UserCircle className="size-6 shrink-0 text-ignite" />
                            <span className="text-sm font-semibold hidden group-hover:inline">Login / Register</span>
                        </Link>
                    )}
                    
                    {!hideLogout && (
                    <Link href="/"className="p-2 text-neutral/50 hover:text-flare rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center group-hover:justify-start gap-4">
                        <LogOut className="size-6 shrink-0" />
                        <span className="text-sm font-semibold hidden group-hover:inline">Logout</span>
                    </Link>
                    )}
                </div>
            </aside>

            <div className="flex-1 flex flex-col min-h-screen overflow-y-auto overflow-x-hidden relative z-10">
                <main className="p-6 flex flex-col w-full max-w-[1800px] mx-auto flex-1">
                    {children}
                </main>
            </div>
        </div>
    );
}

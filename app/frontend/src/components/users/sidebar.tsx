import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { Flame, Map, House, Settings, MessageCircleWarning, MessagesSquare, LogOut } from 'lucide-react';

const mainMenuItems = [
    { label: 'Home', href: '/registeredUser/registeredUserLanding', icon: House },
    { label: 'Report a Fire', href: '/registeredUser/registeredReportFire', icon: Flame },
    { label: 'Fire Simulation', href: '/registeredUser/registeredUnderConstruction', icon: Map },
    { label: 'Notifications', href: '/registeredUser/registeredUnderConstruction', icon: MessageCircleWarning },
    { label: 'Community', href: '/registeredUser/registeredUnderConstruction', icon: MessagesSquare },
];

const settingsMenuItem = [
    { label: 'Settings', href: '/registeredUser/registeredUnderConstruction', icon: Settings },
];

export function SidebarLayout({ children }: { children?: Readonly<React.ReactNode> }) {
    const router = useRouter();

    return (
        <div className="flex min-h-screen bg-carbon-bg text-neutral font-body antialiased relative z-0">
            {/* Atmospheric Background Blooms */}
            <div className="global-atmos">
                <div className="ga-bloom-primary"></div>
                <div className="ga-bloom-secondary"></div>
            </div>

            <aside className="hidden lg:flex flex-col items-center bg-carbon-side border-r border-carbon-card h-screen sticky top-0 z-40 transition-all duration-300 ease-in-out group w-[92px] hover:w-64 shrink-0 shadow-2xl shadow-black/50">
                <div className="relative h-20 w-full mt-6 mb-4 px-2 shrink-0">
                    <div className="absolute inset-0 flex items-center justify-center group-hover:justify-start group-hover:px-4 opacity-100 group-hover:opacity-0 transition-opacity duration-300 ease-in-out">
                        <img src="/images/logo-small.png" alt="FireAway" className="h-12 w-10 object-contain group-hover:hidden"/>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center group-hover:justify-start group-hover:px-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out">
                        <img src="/images/logo-large.png" alt="FireAway" className="h-20 w-48 object-contain hidden group-hover:block mx-auto"/>
                    </div>
                </div>

                <div className="w-full text-center mt-6 mb-2 px-2 shrink-0">
                    <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase block group-hover:hidden whitespace-nowrap">MAIN</span>
                    <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase hidden group-hover:block text-left px-4 whitespace-nowrap">MAIN MENU</span>
                </div>

                <div className="w-full grow overflow-y-auto overflow-x-hidden">
                    <ul className="menu w-full px-3 space-y-3 flex flex-col items-center group-hover:items-start">
                        {mainMenuItems.map(({label, href, icon: Icon}) => {
                            const isActive = router.pathname === href;
                            return (
                                <li className="w-full" key={href}>
                                    <Link href={href} className={`py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left ${isActive ? 'bg-smoke-hover' : ''}`}>
                                        <Icon className={`size-6 shrink-0 transition-colors ${isActive ? 'text-ignite' : 'text-neutral/70 group-hover:text-ignite'}`}/>
                                        <span className="text-sm font-semibold tracking-wide text-neutral hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                                            {label}
                                        </span>
                                    </Link>
                                </li>
                            );
                        })}

                        <div className="w-full text-center mt-4 mb-1 px-2 border-t border-carbon-card pt-4 shrink-0">
                            <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase block group-hover:hidden whitespace-nowrap">SETTINGS</span>
                            <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase hidden group-hover:block text-left px-4 whitespace-nowrap">APP SETTINGS</span>
                        </div>

                        {settingsMenuItem.map(({label, href, icon: Icon}) => {
                            const isActive = router.pathname === href;

                            return(
                                <li className="w-full mt-auto" key={href}>
                                    <Link href={href} className={`py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left ${isActive ? 'bg-smoke-hover' : ''}`}>
                                        <Icon className={`size-6 shrink-0 transition-colors ${isActive ? 'text-ignite' : 'text-neutral/70 group-hover:text-ignite'}`}/>
                                        <span className="text-sm font-semibold tracking-wide text-neutral hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                                            {label}
                                        </span>
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </div>

                <div className="w-full p-4 border-t border-carbon-card flex flex-col items-center gap-4 group-hover:items-start group-hover:px-6 transition-all bg-carbon-side">
                    <button 
                        onClick={async () => {
                            try {
                                await fetch('/api/auth/logout',
                                    {
                                        method: 'POST',
                                        credentials: 'include',
                                    }
                                );
                            } catch (err) {
                                console.error('Logout request failed', err);
                            }
                            router.replace('/login');
                        }}
                        className="p-2 text-neutral/50 hover:text-flare rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center group-hover:justify-start gap-4">
                            <LogOut className="size-6 shrink-0" />
                        <span className="text-sm font-semibold hidden group-hover:inline">Logout</span>
                    </button>
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
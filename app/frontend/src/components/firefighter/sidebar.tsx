import React from 'react';
import { BookAlert, Map, LayoutDashboard, Settings, LogOut } from 'lucide-react';

export function SidebarLayout({ children }: { children?: React.ReactNode }) {
    return (
        <div className="flex min-h-screen bg-carbon-bg text-neutral font-body antialiased relative z-0">
            {/* Atmospheric Background Blooms */}
            <div className="global-atmos">
                <div className="ga-bloom-primary"></div>
                <div className="ga-bloom-secondary"></div>
            </div>

            <aside className="hidden lg:flex flex-col items-center bg-carbon-side border-r border-carbon-card h-screen sticky top-0 z-40 transition-all duration-300 ease-in-out group w-[92px] hover:w-64 shrink-0 shadow-2xl shadow-black/50">
                
                <div className="flex items-center justify-center group-hover:justify-start group-hover:px-4 mt-6 mb-4 px-2 shrink-0 transition-all duration-300 w-full">
                    <img src="/images/logo-small.png" alt="FireAway" className="h-12 w-10 object-contain group-hover:hidden"/>
                    <img src="/images/logo-large.png" alt="FireAway" className="h-20 w-48 object-contain hidden group-hover:block"/>
                </div>

                <div className="w-full text-center mt-6 mb-2 px-2 shrink-0">
                    <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase block group-hover:hidden">MAIN</span>
                    <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase hidden group-hover:block text-left px-4">MAIN MENU</span>
                </div>

                <div className="w-full grow overflow-y-auto overflow-x-hidden">
                    <ul className="menu w-full px-3 space-y-3 flex flex-col items-center group-hover:items-start">
                        <li className="w-full">
                            <button className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left">
                                <LayoutDashboard className="size-6 text-neutral/70 group-hover:text-ignite shrink-0 transition-colors" />
                                <span className="text-sm font-semibold tracking-wide text-neutral hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">Firefighter Dashboard</span>
                            </button>
                        </li>
                        <li className="w-full">
                            <button className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left">
                                <BookAlert className="size-6 text-neutral/70 group-hover:text-ignite shrink-0 transition-colors" />
                                <span className="text-sm font-semibold tracking-wide text-neutral hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">Reported Fires</span>
                            </button>
                        </li>
                        <li className="w-full">
                            <button className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left">
                                <Map className="size-6 text-neutral/70 group-hover:text-ignite shrink-0 transition-colors" />
                                <span className="text-sm font-semibold tracking-wide text-neutral hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">Fire Simulation</span>
                            </button>
                        </li>

                        <div className="w-full text-center mt-4 mb-1 px-2 border-t border-carbon-card pt-4 shrink-0">
                            <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase block group-hover:hidden">SETTINGS</span>
                            <span className="text-[10px] font-bold tracking-widest text-neutral/40 uppercase hidden group-hover:block text-left px-4">SYSTEM SETTINGS</span>
                        </div>

                        <li className="w-full mt-auto">
                            <button className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left">
                                <Settings className="size-6 text-neutral/70 group-hover:text-ignite shrink-0 transition-colors" />
                                <span className="text-sm font-semibold tracking-wide text-neutral hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">Settings</span>
                            </button>
                        </li>
                    </ul>
                </div>

                <div className="w-full p-4 border-t border-carbon-card flex flex-col items-center gap-4 group-hover:items-start group-hover:px-6 transition-all bg-carbon-side">
                    <button className="p-2 text-neutral/50 hover:text-flare rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center group-hover:justify-start gap-4">
                        <LogOut className="size-6 shrink-0" />
                        <span className="text-sm font-semibold hidden group-hover:inline">Log Out System</span>
                    </button>
                </div>
            </aside>

            <div className="flex-1 flex flex-col min-h-screen overflow-x-hidden relative z-10">
                <main className="p-12 grow flex flex-col w-full max-w-[1800px] mx-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}
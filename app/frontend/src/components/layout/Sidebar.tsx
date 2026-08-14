import React from 'react';
import Link from 'next/link';
import { Settings, LogOut, UserCircle } from 'lucide-react';

export function NavLink({ icon: Icon, label, href }: Readonly<{ icon: any; label: string; href?: string }>) {
    const content = (
        <>
            <Icon className="size-5 shrink-0 ml-1 group-hover:ml-6 transition-all" />
            <span className="text-sm font-medium tracking-wide hidden group-hover:inline opacity-0 group-hover:opacity-100 tranistion-opacity duration-200 whitespace-nowrap">
                {label}
            </span>
        </>
    );

    const className =
        "py-2.5 px=4 w-full rounded-lg flex items-center justify-center group-hover:justify-start gap-4 hover:bg-smoke-hover active:scale-[0.98] transition-all text-left text-text-primary hoverLtext-text-primary";

    return href ? (
        <Link href={href} className={className}>
            {content}
        </Link>
    ) : (
        <button type="button" className={className}>
            {content}
        </button>
    );
}

export function SideBar({
    items,
    children,
    hideLogout = false,
    hideLoginRegister = false,
}: Readonly<{
    items: React.ReactNode;
    children?: React.ReactNode;
    hideLogout?: boolean;
    hideLoginRegister?: boolean;
}>) {
  return <div className="flex min-h-screen bg-carbon-bg text-text-primary font-body antialised realtive z-0">
            {/* background */}
            <div className="global-atmos">
                <div className="ga-bloom-primary" />
                <div className="ga-bloom-secondary" />
            </div>

            <aside className="hidden lg:flex flex-col items-center bg-carbon-side border-r border-carbon-card h-screen sticky top-0 z-40 transition-all duration-300 ease-in-out group w-23 hover:w-64 shrink-0 shadow-2xl shadow-black/50">

            {/* logos */}
            <div className="flex items-center justify-center group-hover:justify-start group-hover:px-6 mt-6 mb-4 px-2 shrink-0 transition-all duration-300 w-full">
                <img src="/images/logo-small.png" alt="FireAway" className="h-12 w-10 object-contain group-hover:hidden"/>
                <img src="/images/logo-large.png" alt="FireAway" className="h-20 w-48 object-contain hidden group-hover:block"/>
            </div>

            {/* main nav */}
                <div className="w-full grow overflow-y-auto overflow-x-hidden scrollbar-hide">
                    <ul className="menu w-full px-3 space-y-2 flex flex-col items-center group-hover:items-start">
                        {items}
                    </ul>

                    {/* settings section */}
                    <div className="w-full border-t border-carbon-card bg-carbon-side shrink-0 flex flex-col px-3 py-4 gap-2">
                        <span className="text-[10px] font-bold tracking-widest text-text-primary uppercase block text-center group-hover:hidden">SYS</span>
                        <span className="text-[10px] font-bold tracking-widest text-text-primary uppercase hidden group-hover:block text-left px-2">SYSTEM SETTINGS</span>
                    </div>

                    {!hideLogout && (
                        <button className="py-3 px-4 rounded-xl flex items-center justify-center group-hover:justify-start gap-5 hover:bg-smoke-hover active:scale-[0.98] transition-all w-full text-left">
                            <Settings className="size-6 text-text-primary group-hover:text-ignite shrink-0 transition-colors" />
                            <span className="text-sm font-semibold hidden group-hover:inline opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                            Global Settings
                            </span>
                        </button>
                    )}
                </div>

                {/* footer */}
                <div className="w-full p-4 border-t border-carbon-card flex flex-col items-center gap-2 group-hover:items-start group-hover:px-6 transition-all bg-carbon-side shrink-0">
                    {!hideLoginRegister && (
                        <Link href="/" className="p-2 text-text-primary hover:text-white rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center group-hover:justify-start gap-4">
                            <UserCircle className="size-6 shrink-0 text-ignite" />
                            <span className="text-sm font-semibold hidden group-hover:inline">Login / Register</span>
                        </Link>
                    )}

                    {!hideLogout && (
                        <Link href="/"className="p-2 text-text-primary hover:text-flare rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center group-hover:justify-start gap-4">
                            <LogOut className="size-6 shrink-0" />
                            <span className="text-sm font-semibold hidden group-hover:inline">Logout</span>
                        </Link>
                    )}
                </div>
            </aside>

            <div className="flex-1 flex flex-col min-h-screen overflow-y-auto overflow-x-hidden relative z-10">
                <main className="p-6 flex flex-col w-full max-w-450 mx-auto flex-1">
                    {children}
                </main>
            </div>
        </div>
}

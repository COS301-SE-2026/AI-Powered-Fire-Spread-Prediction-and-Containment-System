import React from 'react';
import Link from 'next/link';
import { LogOut, UserCircle, HelpCircle, Menu } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { headers } from 'next/headers';
import { useRouter } from 'next/router';
import { logout } from '@/lib/api';
import { NavLink } from './NavLink';

export function SideBar({
  items,
  children,
  hideLogout = false,
  hideLoginRegister = true,
}: Readonly<{
  items: React.ReactNode;
  children?: React.ReactNode;
  hideLogout?: boolean;
  hideLoginRegister?: boolean;
}>) {
  const router = useRouter();
  const section = router.pathname.split('/')[1];
  return (
    <div className="drawer lg:drawer-open h-screen">
      <input id="mobile-nav-drawer" type="checkbox" className="drawer-toggle" />

      <div className="drawer-content flex flex-col h-screen min-h-0 overflow-hidden bg-carbon-bg text-text-primary font-body antialiased relative z-0">
        {/* background */}
        <div className="global-atmos">
          <div className="ga-bloom-primary" />
          <div className="ga-bloom-secondary" />
        </div>

        {/* mobile top bar */}
        <div className="lg:hidden flex items-center justify-between px-4 py-3 border-b bg-carbon-side border-carbon-card sticky top-0 z-40">
          <img
            src="/images/logo-small.png"
            alt="FireAway"
            className="h-8 w-auto object-contain"
          />
          <label htmlFor='mobile-nav-drawer' className='btn btn-ghost btn-circle'>
            <Menu className='size-6 text-text-primary' />
          </label>
        </div>

        <div className="flex flex-1 min-h-0">
          <div className="flex-1 min-h-0 flex flex-col overflow-y-auto overflow-x-hidden relative z-10">
            <main className="p-2 flex flex-col w-full max-w-450 mx-auto flex-1 min-h-0">{children}</main>
          </div>
        </div>
      </div>

      {/* desktop */}
      <div className='drawer-side z-50'>
        <label htmlFor='mobile-nav-drawer' aria-label='close sidebar' className='drawer-overlay'/>

        <aside className="flex flex-col items-center bg-carbon-side border-r border-carbon-card h-screen w-64 lg:w-23 lg:hover:w-64 transition-all duration-300 ease-in group shrink-0 shadow-2xl shadow-black/50">
          {/* logos */}
          <div className='flex items-center justify-center group-hover:px-6 mt-6 mb-4 px-2 shrink-0 transition-all duration-300 w-full'>
            <img
              src="/images/logo-small.png"
              alt="FireAway"
              className="h-12 w-10 object-contain hidden lg:block lg:group-hover:hidden"
            />
            <img
              src="/images/logo-large.png"
              alt="FireAway"
              className="h-20 w-48 object-contain block lg:hidden lg:group-hover:block"
            />
          </div>

          {/* main nav */}
          <div className="w-full grow overflow-y-auto overflow-x-hidden scrollbar-hide">
            <ul className="menu w-full px-3 space-y-2 flex flex-col items-center lg:group-hover:items-start">
              {items}
            </ul>
          </div>

        {/* footer */}
        <div className="w-full p-4 border-t border-carbon-card flex flex-col items-center gap-2 group-hover:items-start group-hover:px-6 transition-all bg-carbon-side shrink-0">

          <NavLink icon={HelpCircle} label="Help Menu" href={`/${section}/Help`} />

          {!hideLoginRegister && (
            <Link
              href="/login"
              className="p-2 text-text-primary hover:text-white rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-center lg:justify-center lg:group-hover:justify-start gap-4"
            >
              <UserCircle className="size-6 shrink-0 text-ignite" />
              <span className="text-sm font-semibold inline lg:hidden lg:group-hover:inline">
                Login / Register
              </span>
            </Link>
          )}

            {!hideLogout && (
              <button
                onClick = {() => {
                  logout();
                }}
                className="p-2 text-text-primary hover:text-flare rounded-lg hover:bg-smoke-hover transition-colors w-full flex items-center justify-start gap-4"
              >
                <LogOut className="size-6 shrink-0" />
                <span className="text-sm font-semibold inline lg:hidden lg:group-hover:inline">Logout</span>
              </button>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

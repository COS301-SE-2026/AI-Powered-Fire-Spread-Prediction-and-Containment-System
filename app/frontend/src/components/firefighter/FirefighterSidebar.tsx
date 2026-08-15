import React from 'react';
import { SideBar } from '../layout/SideBar';
import { FirefighterItems } from './FirefighterItems';

export function FirefighterSideBar({
  children,
  hideLogout = false,
  hideLoginRegister = false,
}: Readonly<{
  children?: React.ReactNode;
  hideLogout?: boolean;
  hideLoginRegister?: boolean;
}>) {
  return (
    <SideBar
      items={<FirefighterItems />}
      hideLogout={hideLogout}
      hideLoginRegister={hideLoginRegister}
    >
      {children}
    </SideBar>
  );
}

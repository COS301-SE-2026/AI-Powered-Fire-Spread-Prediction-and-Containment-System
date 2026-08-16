import React from 'react';
import { SideBar } from '../layout/SideBar';
import { AdminItems } from './AdminItems';

export function AdminSideBar({
  children,
  hideLogout = false,
  hideLoginRegister = false,
}: Readonly<{
  children?: React.ReactNode;
  hideLogout?: boolean;
  hideLoginRegister?: boolean;
}>) {
  return (
    <SideBar items={<AdminItems />} hideLogout={hideLogout} hideLoginRegister={hideLoginRegister}>
      {children}
    </SideBar>
  );
}

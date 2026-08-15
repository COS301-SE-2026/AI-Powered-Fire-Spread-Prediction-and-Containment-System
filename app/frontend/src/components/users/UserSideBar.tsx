import React from 'react';
import { SideBar } from '../layout/SideBar';
import { UserItems } from './UserItems';

export function UserSideBar({
  children,
  hideLogout = false,
  hideLoginRegister = false,
}: Readonly<{
  children?: React.ReactNode;
  hideLogout?: boolean;
  hideLoginRegister?: boolean;
}>) {
  return (
    <SideBar items={<UserItems />} hideLogout={hideLogout} hideLoginRegister={hideLoginRegister}>
      {children}
    </SideBar>
  );
}

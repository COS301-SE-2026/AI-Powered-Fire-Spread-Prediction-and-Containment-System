import React from 'react';
import { useNotifications } from '../../hooks/useNotification';
import { NotificationToast } from './NotificationToast';

export function NotificationToastHost() {
  const { activeToast, dismissToast } = useNotifications();

  if (!activeToast) return null;

  return (
    <div className='toast toast-top toast-end z-[200] mt-14'>
      <NotificationToast notification={activeToast} onDismiss={dismissToast} />
    </div>
  );
}

import React from 'react';
import { useNotifications } from '../../hooks/useNotification';
import { NotificationToast } from './NotificationToast';

export function NotificationToastHost() {
  const { activeToast, dismissToast } = useNotifications();

  if (!activeToast) return null;

  return (
    <div className="fixed top-4 right-4 z-50">
      <NotificationToast notification={activeToast} onDismiss={dismissToast} />
    </div>
  );
}

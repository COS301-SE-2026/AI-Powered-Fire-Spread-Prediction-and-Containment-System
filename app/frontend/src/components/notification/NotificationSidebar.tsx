import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { createPortal } from 'react-dom';
import type { FireNotification } from '../../types/Notifications';
import { NotificationCard } from './NotificationCard';

interface NotificationSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: readonly FireNotification[];
  onRead: (id: string) => void;
}

export function NotificationSidebar({
  isOpen,
  onClose,
  notifications,
  onRead,
}: Readonly<NotificationSidebarProps>) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if(!mounted || !isOpen) return null;

  const visibleNotifications = mounted ? notifications : [];

  return createPortal(
    <div role="dialog" aria-modal="true" aria-label="Notifications" className="fixed inset-0 z-50" style={{ paddingTop: 'env(safe-area-inset-top)' }}>

      <button
        type="button"
        onClick={onClose}
        aria-label="Close notifications"
        className="absolute inset-0 bg-black/50 transition-opacity duration-200 opacity-100"
      />

    <div className="absolute right-0 top-0 h-full w-80 max-w-[85vw] bg-carbon-side p-4 flex flex-col shadow-xl transition-transform duration-200 translate-x-0">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-text-primary font-bold uppercase text-medium">Notifications</h2>
        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded-full hover:bg-white/10 text-text-primary"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {visibleNotifications.length === 0 ? (
          <p className="text-sm text-text-muted text-center mt-8">No notifications currently</p>
        ) : (
          notifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onRead={onRead}
            />
          ))
        )}
      </div>
    </div>
  </div>,
  document.body
  );
}

import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
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

  const visibleNotifications = mounted ? notifications : [];

  return (
    <div className={`drawer drawer-end fixed inset-0 z-50 ${isOpen ? '' : 'pointer-events-none'}`}>
      <input type="checkbox" className="drawer-toggle" checked={isOpen} readOnly />

      <div className="drawer-side">
        <button
          type="button"
          onClick={onClose}
          aria-label="Close notifications"
          className="drawer-overlay btn btn-link"
        />

        <div className="menu w-80 h-full bg-carbon-side p-4 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-text-primary font-bold uppercase text-sm">Notifications</h2>
            <button
              onClick={onClose}
              className="btn btn-ghost btn-circle btn-sm"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {visibleNotifications.length === 0 ? (
              <p className="text-xs text-text-muted text-center mt-8">No notifications currently</p>
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
      </div>
    </div>
  );
}

import React, { createContext, useContext, useState, useMemo, useCallback } from 'react';
import type { FireNotification } from '../types/Notifications';

const MOCK_NOTIFICATIONS: readonly FireNotification[] = [
  {
    id: '1',
    fireLocation: 'Groenkloof Nature Reserve',
    distance: 4.6,
    type: 'alert',
    severity: 'high',
    message: 'Nearby fire reported',
    fireId: '1',
    time: '2026-08-11T10:00:00Z',
    read: false,
  },
  {
    id: '2',
    fireLocation: 'Voortrekker Monument hillside',
    distance: 6.4,
    type: 'update',
    severity: 'moderate',
    message: 'Firefighters are on their way',
    fireId: '2',
    time: '2026-08-10T15:30:00Z',
    read: false,
  },
  {
    id: '3',
    fireLocation: 'Fountains Valley Recreation Resort',
    distance: 1.2,
    type: 'alert',
    severity: 'extreme',
    message: 'Nearby fire reported',
    fireId: '3',
    time: '2026-08-12T08:45:00Z',
    read: false,
  },
  {
    id: '4',
    fireLocation: 'Menlyn Maine construction site',
    distance: 3.8,
    type: 'update',
    severity: 'high',
    message: 'Fire has moved closer, distance updated',
    fireId: '4',
    time: '2026-08-12T09:10:00Z',
    read: false,
  },
  {
    id: '5',
    fireLocation: 'Pretoria National Botanical Garden',
    distance: 9.1,
    type: 'alert',
    severity: 'low',
    message: 'Nearby fire reported',
    fireId: '5',
    time: '2026-08-09T14:20:00Z',
    read: true,
  },
  {
    id: '6',
    fireLocation: 'LC de Villiers Sports Grounds, Hatfield',
    distance: 1.4,
    type: 'update',
    severity: 'extreme',
    message: 'Containment line established nearby',
    fireId: '6',
    time: '2026-08-12T07:55:00Z',
    read: false,
  },
  {
    id: '7',
    fireLocation: 'Lynnwood Road crossing',
    distance: 2.5,
    type: 'update',
    severity: 'low',
    message: 'Fire contained, risk reduced',
    fireId: '7',
    time: '2026-08-08T18:00:00Z',
    read: true,
  },
];

type NotificationState = Readonly <{
    notifications: readonly FireNotification[];
    unreadCount: number;
    isLoading: boolean;
    error: string | null;
    markAsRead: (id: string) => void;
    activeToast: FireNotification | null;
    showToast: (notification: FireNotification) => void;
    dismissToast: () => void;
    previewToast: (notification: FireNotification) => void;
}>;

const NotificationsContext = createContext<NotificationState | null>(null);

export function NotificationsProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [notifications, setNotifications] = useState<readonly FireNotification[]>(MOCK_NOTIFICATIONS);
  const [isLoading] = useState(false);
  const [error] = useState<string | null>(null);
  const [activeToast, setActiveToast] = useState<FireNotification | null>(null);

  const showToast = useCallback((notification: FireNotification): void => {
    setNotifications((prev) => [notification, ...prev]);
    setActiveToast(notification);
  }, []);

  const dismissToast = useCallback((): void => {
    setActiveToast(null);
  }, []);

  const previewToast = useCallback((notification: FireNotification): void => {
    setActiveToast(notification);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAsRead = useCallback((id: string): void => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    );
  }, []);

  const value = useMemo(
    () => ({
      notifications,
      unreadCount,
      isLoading,
      error,
      markAsRead,
      activeToast,
      showToast,
      dismissToast,
      previewToast,
    }),
    [notifications, unreadCount, isLoading, error, markAsRead, activeToast, showToast, dismissToast, previewToast],
  );

  return (
    <NotificationsContext.Provider value={value}>
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications(): NotificationState {
    const context = useContext(NotificationsContext);
    if (!context) {
      throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
}
import { useState } from 'react';
import type { FireNotification } from '../types/Notifications';

const MOCK_NOTIFICATIONS: readonly FireNotification[] = [
  {
    id: '1',
    fireLocation: 'Groenkloof Nature Reserve',
    distance: 4.6,
    type: 'alert',
    severity: 'high',
    mapDeepLink: '/users/live-map?fire=1',
    time: '2026-08-11T10:00:00Z',
    read: false,
  },
  {
    id: '2',
    fireLocation: 'Voortrekker Monument hillside',
    distance: 6.4,
    type: 'update',
    severity: 'moderate',
    mapDeepLink: '/users/live-map?fire=2',
    time: '2026-08-10T15:30:00Z',
    read: false,
  },
];

type NotificationState = Readonly <{
    notifications: readonly FireNotification[];
    unreadCount: number;
    isLoading: boolean;
    error: string | null;
    markAsRead: (id: string) => void;
}>;

export function useNotifications(): NotificationState {
    const [notifications, setNotifications] = useState<readonly FireNotification[]>(MOCK_NOTIFICATIONS);
    const [isLoading] = useState(false);
    const [error] = useState<string | null>(null);

    const unreadCount = notifications.filter((n) => !n.read ).length;

    const markAsRead = (id: string): void => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
        );
    };

    return { notifications, unreadCount, isLoading, error, markAsRead };
}
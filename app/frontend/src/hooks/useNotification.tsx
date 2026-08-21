import React, { createContext, useContext, useState, useMemo, useCallback, useEffect, useRef } from 'react';
import type { FireNotification } from '../types/Notifications';

type NotificationState = Readonly <{
    notifications: readonly FireNotification[];
    unreadCount: number;
    locationEnabled: boolean;
    isLoading: boolean;
    error: string | null;
    markAsRead: (id: string) => void;
    activeToast: FireNotification | null;
    showToast: (notification: FireNotification) => void;
    dismissToast: () => void;
    previewToast: (notification: FireNotification) => void;
}>;

const NotificationsContext = createContext<NotificationState | null>(null);

interface NotificationListResponse {
  notifications: FireNotification[];
  unread_count: number;
  locationEnabled: boolean;
}

export function NotificationsProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [notifications, setNotifications] = useState<readonly FireNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [locationEnabled, setLocationEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeToast, setActiveToast] = useState<FireNotification | null>(null);

  const showToast = useCallback((notification: FireNotification): void => {
    setActiveToast(notification);
  }, []);

  const dismissToast = useCallback((): void => {
    setActiveToast(null);
  }, []);

  const previewToast = useCallback((notification: FireNotification): void => {
    setActiveToast(notification);
  }, []);


  // initial load: recent notification history, unread count, whether user has location on file at all
  useEffect(() => {
    let cancelled = false;

    async function fetchNotifications() {
      try {
        const res = await fetch('/api/notifications', { credentials: 'include' });
        if (!res.ok) throw new Error (`Failed to load notifications (${res.status})`);
        const data: NotificationListResponse = await res.json();
        if (cancelled) return;

        setNotifications(data.notifications);
        setUnreadCount(data.unread_count);
        setLocationEnabled(data.locationEnabled);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to load notifications');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchNotifications();
    return () => {
      cancelled = true;
    };
  }, []);

  // Live push over WebSocket. Auth comes from same access_token cookie
  // REST calls use, browsers attach it to WS handshake automatically so no token neeeds to be passed here
  useEffect(() => {
    const protocol = window.location.protocol === 'https' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/notifications/ws`);

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event !== 'notification') return;

        const incoming = payload.data as FireNotification;
        setNotifications((prev) => [incoming, ...prev]);
        setUnreadCount((prev) => prev + 1);
        showToast(incoming);
      } catch (err) {
        console.warn('Failed to parse notification payload', err);
      }
    };

    ws.onerror = (err) => {
      console.warn('Notifications WebSocket error', err);
    };

    return () => {
      ws.close();
    };
  }, [showToast]);

  const markAsRead = useCallback((id: string): void => {
    // optimistic local update (UI reflects 'read' immediately rather than waitng on network round trip)
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    );
    setUnreadCount((prev) => Math.max(0, prev - 1));

    fetch(`/api/notifications/${id}/read`, {
      method: 'POST',
      credentials: 'include',
    }).catch((err) => {
      console.warn('Failed to mark notifications as read', err);
    });
  }, []);

  const value = useMemo(
    () => ({
      notifications,
      unreadCount,
      locationEnabled,
      isLoading,
      error,
      markAsRead,
      activeToast,
      showToast,
      dismissToast,
      previewToast,
    }),
    [notifications, unreadCount, locationEnabled, isLoading, error, markAsRead, activeToast, showToast, dismissToast, previewToast],
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
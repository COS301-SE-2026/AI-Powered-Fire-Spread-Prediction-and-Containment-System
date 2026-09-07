import React, {
  createContext,
  useContext,
  useState,
  useMemo,
  useCallback,
  useEffect,
  useRef,
} from 'react';
import type { FireNotification } from '../types/Notifications';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

const PANEL_RETENTION_MS = 24 * 60 * 60 * 1000;

function isWithinRetention(time: string): boolean {
  return Date.now() - new Date(time).getTime() < PANEL_RETENTION_MS;
}

function getWebSocketUrl(path: string): string {
  const httpBase = API_URL || window.location.origin;
  return httpBase.replace(/^http/, 'ws') + path;
}

type NotificationState = Readonly<{
  notifications: readonly FireNotification[];
  unreadCount: number;
  locationEnabled: boolean;
  isLoading: boolean;
  error: string | null;
  markAsRead: (id: string) => void;
  refetchAfterAction: () => Promise<void>;
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
  const [locationEnabled, setLocationEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeToast, setActiveToast] = useState<FireNotification | null>(null);
  const knownIdsRef = useRef<Set<string>>(new Set());
  const dismissIsRef = useRef<Set<string>>(new Set());

  const showToast = useCallback((notification: FireNotification): void => {
    setActiveToast(notification);
  }, []);

  const dismissToast = useCallback((): void => {
    setActiveToast(null);
  }, []);

  const previewToast = useCallback((notification: FireNotification): void => {
    setActiveToast(notification);
  }, []);

  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.read && isWithinRetention(n.time)).length,
    [notifications]
  );

  // periodically drops notifications older than 24h retention window
  useEffect(() => {
    const interval = setInterval(() => {
      setNotifications((prev) => {
        const kept = prev.filter((n) => isWithinRetention(n.time));
        return kept;
      });
    }, 60_000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    knownIdsRef.current = new Set(notifications.map((n) => n.id));
  }, [notifications]);

  const fetchNotifications = useCallback(
    async (options: { toastIfNew: boolean }) => {
      try {
        const res = await fetch('/api/notifications', { credentials: 'include' });
        if (!res.ok) throw new Error(`Failed to load notifications (${res.status})`);
        const data: NotificationListResponse = await res.json();

        const previouslyKnown = knownIdsRef.current;
        const newlyArrived = data.notifications.filter((n) => !previouslyKnown.has(n.id));

        setNotifications(data.notifications);
        knownIdsRef.current = new Set(data.notifications.map((n) => n.id));
        setLocationEnabled(data.locationEnabled);
        setError(null);

        if (options.toastIfNew) {
          const toastCandidate =
            newlyArrived.find((n) => !n.read && !dismissIsRef.current.has(n.id)) ??
            data.notifications.find((n) => !n.read && !dismissIsRef.current.has(n.id));

          if (toastCandidate) {
            showToast(toastCandidate);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load notifications');
      } finally {
        setIsLoading(false);
      }
    },
    [showToast]
  );

  const refetchAfterAction = useCallback(async () => {
    await fetchNotifications({ toastIfNew: true });
  }, [fetchNotifications]);

  // initial load: recent notification history, unread count, whether user has location on file at all
  useEffect(() => {
    let cancelled = false;

    async function initialLoad() {
      const justLoggedIn = sessionStorage.getItem('justLoggedIn') === '1';
      if (justLoggedIn) {
        sessionStorage.removeItem('justLoggedIn');
      }

      if (!cancelled) {
        await fetchNotifications({ toastIfNew: justLoggedIn });
      }
    }

    initialLoad();
    return () => {
      cancelled = true;
    };
  }, [fetchNotifications]);

  // Live push over WebSocket. Auth comes from same access_token cookie
  // REST calls use, browsers attach it to WS handshake automatically so no token neeeds to be passed here
  useEffect(() => {
    const ws = new WebSocket(getWebSocketUrl('/api/notifications/ws'));

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event !== 'notification') return;

        const incoming = payload.data as FireNotification;
        if (knownIdsRef.current.has(incoming.id)) {
          return; // already have it - skip, don't re-toast a duplicate
        }
        knownIdsRef.current.add(incoming.id);

        setNotifications((prev) => [incoming, ...prev]);
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
    dismissIsRef.current.add(id);
    // optimistic local update (UI reflects 'read' immediately rather than waitng on network round trip)
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));

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
      refetchAfterAction,
      activeToast,
      showToast,
      dismissToast,
      previewToast,
    }),
    [
      notifications,
      unreadCount,
      locationEnabled,
      isLoading,
      error,
      markAsRead,
      refetchAfterAction,
      activeToast,
      showToast,
      dismissToast,
      previewToast,
    ]
  );

  return <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>;
}

export function useNotifications(): NotificationState {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

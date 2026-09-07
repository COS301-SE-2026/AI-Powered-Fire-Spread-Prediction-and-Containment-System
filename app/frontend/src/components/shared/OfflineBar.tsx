import React, { useEffect, useState, useRef } from 'react';
import { probeHealth } from '../../lib/offline/shared';
import { offlineStore } from '../../lib/offlineStore';

export const OfflineBar: React.FC = () => {
  const [isOffline, setIsOffline] = useState(false);
  const [queueCount, setQueueCount] = useState(0);
  const failCountRef = useRef(0);
  const lastFailRef = useRef(0);

  const checkStatus = async () => {
    if (typeof window === 'undefined') return;
    
    if (!navigator.onLine) {
      setIsOffline(true);
      const queued = await offlineStore.getQueuedActions();
      setQueueCount(queued.length);
      return;
    }

    const now = Date.now();
    const recentlyFailed = failCountRef.current > 0 && now - lastFailRef.current < 10000;
    if (recentlyFailed) {
      const queued = await offlineStore.getQueuedActions();
      setQueueCount(queued.length);
      return;
    }

    const reachable = await probeHealth();
    if (reachable) {
      failCountRef.current = 0;
      setIsOffline(false);
    } else {
      failCountRef.current += 1;
      if (failCountRef.current >= 2) {
        setIsOffline(true);
      }
    }
    const queued = await offlineStore.getQueuedActions();
    setQueueCount(queued.length);
  };

  useEffect(() => {
    checkStatus();

    const handleOnline = async () => {
      setIsOffline(false);
      failCountRef.current = 0;

      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await offlineStore.syncQueuedActions(apiBaseUrl);
      const queued = await offlineStore.getQueuedActions();
      setQueueCount(queued.length);
    };

    const handleOffline = () => {
      setIsOffline(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    const interval = setInterval(checkStatus, 15000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  if (!isOffline && queueCount === 0) {
    return null;
  }

  return (
    <aside
      role="status"
      aria-live="polite"
      className="fixed bottom-0 left-0 right-0 z-50 bg-amber-600 text-white px-4 py-2 flex items-center justify-between shadow-lg text-sm font-medium"
    >
      <div className="flex items-center space-x-2">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
        <span>
          {isOffline
            ? 'Offline! You are viewing outdated incidents and predictions'
            : 'Online: Now syncing offline data'}
        </span>
      </div>
      {queueCount > 0 && (
        <span className="bg-amber-800 text-xs px-2.5 py-1 rounded-full font-mono">
          {queueCount} queued
        </span>
      )}
    </aside>
  );
};

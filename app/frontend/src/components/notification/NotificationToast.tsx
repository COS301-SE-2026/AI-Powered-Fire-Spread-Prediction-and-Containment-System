import { useEffect } from 'react';
import { AlertTriangle, Bell, RefreshCw, X } from 'lucide-react';
import Link from 'next/link';
import type { FireNotification } from '../../types/Notifications';
import { FormatDate } from '../../lib/FormatDate';
import { useAuth } from '../../hooks/useAuth';
import { NotificationLink } from './NotificationLink';

const AUTO_DISMISS_MS = 6000;

type NotificationToastProps = Readonly<{
  notification: FireNotification;
  onDismiss: () => void;
}>;

const TOAST_STYLE: Record<FireNotification['type'], string> = {
  alert: 'border-error bg-carbon-side',
  update: 'border-info bg-carbon-side',
};

export function NotificationToast({ notification, onDismiss }: NotificationToastProps) {
  const { role } = useAuth();
  const { type, fireLocation, distance, message, fireId, time } = notification;
  const mapLink = NotificationLink(fireId, role);
  const isLive = mapLink.startsWith('/admin/live-map');

  useEffect(() => {
    const timer = setTimeout(onDismiss, AUTO_DISMISS_MS);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  let icon;
  let headline: string;
  if (type === 'alert') {
    icon = <AlertTriangle className="h-5 w-5 text-error" aria-hidden="true" />;
    headline = 'Fire Alert!';
  } else {
    icon = <RefreshCw className="h-5 w-5 text-info" aria-hidden="true" />;
    headline = `Fire Update: ${message}`;
  }

  const linkContent = (
    <>
      <h3 className="text-sm font-semibold text-text-primary">{headline}</h3>
      <p className="text-xs text-text-primary">{fireLocation}</p>
      <p className="text-xs text-text-primary">
        {distance} km | {FormatDate(time)}
      </p>
      <p className="text-xs font-semibold text-error underline mt-1">View on map</p>
    </>
  );

  return (
    <div className={`alert border-2 shadow-lg max-w-72 ${TOAST_STYLE[type]}`}>
      {icon}
      {isLive ? (
        <a href={mapLink} onClick={onDismiss} className="flex-1">
          {linkContent}
        </a>
      ) : (
        <Link href={mapLink} onClick={onDismiss} className="flex-1">
          {linkContent}
        </Link>
      )}
      <button
        type="button"
        onClick={onDismiss}
        className="btn btn-ghost btn-circle btn-xs"
        aria-label="Dismiss"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  );
}

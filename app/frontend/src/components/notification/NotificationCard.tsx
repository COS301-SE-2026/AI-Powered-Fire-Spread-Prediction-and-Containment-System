import { Bell, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import type { FireNotification } from '../../types/Notifications';
import { NotificationBadge } from './StatusBadge';
import { FormatDate } from '../shared/FormatDate';
import { useAuth } from '../../hooks/useAuth';
import { NotificationLink } from './NotificationLink';

interface NotificationCardProps {
    readonly notification: FireNotification;
    readonly onRead: (id: string) => void;
}

export function NotificationCard({ notification, onRead }: NotificationCardProps){
    const { role } = useAuth();
    const mapLink = NotificationLink(notification.fireId, role);

    const { id, fireLocation, distance, type, severity, fireId, message, time, read } = notification;

    let icon;
    let headline: string;
    if (type === 'alert') {
        icon = <Bell className="h-4 w-4 text-text-primary" aria-hidden="true" />;
        headline ="Fire Alert!";
    } else {
        icon = <RefreshCw className="h-4 w-4 text-text-info" aria-hidden="true" />;
        headline = `Fire Update: ${notification.message}`;
    }

    const handleClick = (): void => {
        if (!read) {
            onRead(id);
        }
    };

    return (
        <Link href={mapLink} onClick={handleClick} className={`flex items-center justify-between border-b border-border-subtle py-3 transition-colors hover:bg-surface-hover ${read ? 'opacity-60' : ''}`}>
            <div className="flex items-start gap-3">{icon}
                <div>
                    <h3 className="text-sm font-semibold text-text-primary">{headline}</h3>
                    <p className="text-sm text-text-muted">{fireLocation}</p>
                    <p className="text-xs text-text-muted">{distance} km | {FormatDate(time)}</p>
                </div>
            </div>
            <NotificationBadge severity={severity} />
        </Link>
    );
}
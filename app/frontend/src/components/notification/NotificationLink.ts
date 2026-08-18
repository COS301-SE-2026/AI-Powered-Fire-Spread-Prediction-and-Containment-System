import type { UserRole } from '../../types/User';

export function NotificationLink(fireId: string, role: UserRole | null): string {
    if (role === 'admin'){
        return `/admin/live-map?fire=${fireId}`;
    }
    if (role === 'firefighter'){
        return `/firefighter/dashboard?fire=${fireId}`;
    }
    return `/user/live-map?fire=${fireId}`;
}
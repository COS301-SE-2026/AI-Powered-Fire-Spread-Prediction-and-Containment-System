import { useAuth } from '@/hooks/useAuth';
import type { UserRole } from '../../types/User';

export function NotificationLink(fireId: string, role: UserRole | null): string {
  switch(role){
    case 'admin':
      return `/admin/live-map?fire=${fireId}`;
    case 'firefighter':
      return `/firefighter/dashboard?fire=${fireId}`;
    case 'user':
      return `/users/live-map?fire=${fireId}`;
    default:
      return `/guests/live-map?fire=${fireId}`;
  }
}

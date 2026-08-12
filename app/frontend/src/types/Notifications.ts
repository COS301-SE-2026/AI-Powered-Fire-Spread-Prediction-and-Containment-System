export type NotificationType = 'alert' | 'update';
export type NotificationSeverity = 'low' | 'moderate' | 'high' | 'extreme';

export type FireNotification = Readonly <{
    id: string;
    fireLocation: string;
    distance: number;
    type: NotificationType;
    severity: NotificationSeverity;
    mapDeepLink: string;
    time: string;
    read: boolean;
}>;
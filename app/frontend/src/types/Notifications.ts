export type NotificationType = 'alert' | 'update';
export type NotificationSeverity = 'low' | 'moderate' | 'high' | 'extreme';

export type FireNotification = Readonly <{
    id: string;
    fireLocation: string;
    distance: number;
    type: NotificationType;
    severity: NotificationSeverity;
    message: string;
    fireId: string;
    time: string;
    read: boolean;
}>;

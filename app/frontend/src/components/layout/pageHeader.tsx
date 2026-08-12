import React, { useState } from "react";
import { Bell, User } from "lucide-react";
import { useRouter } from "next/router";
import { useAuth } from "../../hooks/useAuth";
import { useNotifications } from "../../hooks/useNotification";
import { NotificationSidebar } from "./NotificationSidebar";
import { FireNotification } from "../../types/Notifications";

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
}

const UNREAD_COUNT = 9;

export function PageHeader({title, subtitle, actions }: Readonly<PageHeaderProps>){
    const { isAuth } = useAuth();
    const { unreadCount, notifications } = useNotifications();
    const router = useRouter();
    const [isNotifOpen, setIsNotifOpen] = useState(false);

    const count = unreadCount > UNREAD_COUNT ? `${UNREAD_COUNT}+` : unreadCount;
    const authLabel = isAuth ? 'Profile' : 'Login / Register';

    const handleAuthClick = (): void => {
        router.push(isAuth ? '/profile' : '/login');
    };

    return(
        <>
        <header className="mb-4 flex items-center justify-between">
            <div>
                <h1 className=" text-text-primary uppercase">
                    {title}
                </h1>
                {subtitle && (
                    <h4 className="text-text-muted mt-0.5 ">
                        {subtitle}
                    </h4>
                )}
            </div>
            <div className="flex items-center gap-2">
                {actions}
                {isAuth && (
                    <div className="indicator">
                        {unreadCount > 0 && (
                            <span className="indicator-item badge badge-primary badge-xs w-5 h-5 min-w-5 p-2 rounded-full flex items-center justify-center text-text-primary">
                                {count}
                            </span>
                        )}
                        <button type="button" onClick={() => setIsNotifOpen(true)} className="btn btn-ghost btn-circle" aria-label="Notifications">
                            <Bell className="h-5 w-5 text-text-primary" aria-hidden="true" />
                        </button>
                    </div>
                )}
                <button type="button" onClick={handleAuthClick} className="btn btn-ghost btn-circle" aria-label={authLabel}>
                    <User className="h-5 w-5 text-text-primary" aria-hidden="true" />
                </button>
            </div>
        </header>
        <NotificationSidebar isOpen={isNotifOpen} onClose={() => setIsNotifOpen(false)} notifications={notifications} />
        </>
    );
}
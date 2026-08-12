import React from 'react';
import { X } from 'lucide-react';
import type { FireNotification } from '../../types/Notifications';

interface NotificationSidebarProps {
    isOpen: boolean;
    onClose: () => void;
    notifications: readonly FireNotification[];
}

export function NotificationSidebar({ isOpen, onClose, notifications }: Readonly<NotificationSidebarProps>){
    return (
        <div className={`drawer drawer-end fixed inset-0 z-50 ${isOpen ? '' : 'pointer-events-none'}`}>
            <input type="checkbox" className="drawer-toggle" checked={isOpen} readOnly />

            <div className="drawer-side">
                <label onClick={onClose} className="drawer-overlay" />

                <div className="menu w-80 h-full bg-carbon-side p-4 flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-text-primary font-bold uppercase text-sm">Notifications</h2>
                        <button onClick={onClose} className="btn btn-ghost btn-circle btn-sm" aria-label="Close">
                            <X className="h-5 w-5"/>
                        </button>
                    </div>

                </div>
            </div>
        </div>
    );
}
import React from 'react';

interface RoleRowProps {
    icon: React.ReactNode;
    title: string;
    actions: React.ReactNode;
}

export function RoleRow({ icon, title, actions }: RoleRowProps){
    return (
        <div className='flex items-center justify-between gap-4 py-4 border-b border-carbon-stroke last:border-b-0'>
            <div className="flex items-center gap-3">
                <span className="text-text-muted">{icon}</span>
                <p className='text-text-primary font-semibold'>{title}</p>
            </div>
            {actions}
        </div>
    );
}
import React from 'react';

export function SkeletonRegion({
    label = 'loading',
    className,
    children,
}: Readonly<{ label?: string; className?: string; children: React.ReactNode}>) {
    return (
        <div role='status' aria-busy='true' aria-live='polite' className={className}>
            <span className='sr-only'>{label}</span>
            {children}
        </div>
    );
}
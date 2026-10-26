import React from 'react';
import { cx } from '@/lib/cx';

export function SkeletonCard({
    className = undefined,
    children = undefined,
}: Readonly<{ className?: string; children?: React.ReactNode}>) {
    return (
        <div
            aria-hidden='true'
            className={cx('rounded-2xl border border-carbon-stroke bg-carbon-side/30 p-4 flex flex-col gap-3', className)}
        >
            {children}
        </div>
    );
}
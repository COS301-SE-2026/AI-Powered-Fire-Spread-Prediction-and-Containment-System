import { cx } from "@/lib/cx";
import { Skeleton } from "./Skeleton";

export function SkeletonMapBody({
    className,
    label,
}: Readonly<{ className?: string; label?: string }>) {
    return (
        <div
            aria-hidden='true'
            className={cx('relative w-full h-full min-h-64 rounded-2xl border border-carbon-stroke bg-carbon-side/30 overflow-hidden', className)}
        >
            {/* header bar */}

            <div className='absolute top-0 inset-x-0 flex items-center justify-between p-3 md:p-4 border-b border-carbon-card bg-carbon-bg/50'>
                <Skeleton className='h-4 w-26' />
                <Skeleton className='h-6 w-24 rounded-full' />
            </div>
            {/* floating controls */}
            <Skeleton className='absolute top-16 right-4 h-20 w-28 rounded-xl' />
            <Skeleton className='absolute bottom-6 right-4 size-11 rounded-full' />
            {label ? (
                <div className='absolute inset-0 flex items-center justify-center'>
                    <span className='text-text-primary/40 font-display tracking-widest text-sm uppercase'>
                        {label}
                    </span>
                </div>
            ) : null}
        </div>
    );
}
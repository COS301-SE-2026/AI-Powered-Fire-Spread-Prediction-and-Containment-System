import { SkeletonListBody } from './SkeletonListBody';
import { Skeleton } from './Skeleton';

export function SkeletonSidePanel({
    rows = 4,
    className = undefined,
    panelClassName = undefined,
}: Readonly<{ rows?: number; className?: string; panelClassName?: string }>) {
    return (
        <div aria-hidden='true' className={`flex flex-col gap-2 ${className ?? ''}`}>
            <Skeleton className='h-5 w-36 shrink-0' />
            <div className={`rounded-2xl bg-carbon-side/40 border border-carbon-card overflow-hidden p-2 ${panelClassName ?? ''}`}>
                <SkeletonListBody rows={rows} />
            </div>
        </div>
    );
}
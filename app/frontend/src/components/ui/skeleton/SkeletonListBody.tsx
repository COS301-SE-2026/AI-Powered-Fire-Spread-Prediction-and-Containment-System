import { cx } from "@/lib/cx";
import { Skeleton } from "./Skeleton";

export function SkeletonListBody({
    rows = 4,
    className,
}: Readonly<{ rows?: number; className?: string }>) {
    return (
        <div aria-hidden='true' className={cx('flex flex-col gap-3', className)}>
            {Array.from({ length: rows }, (_, i) => (
                <div
                    key={i}
                    className='rounded-xl border border-carbon-stroke bg-carbon-side/30 p-3 flex items-center gap-3'
                >
                    <Skeleton className='size-10 rounded-lg shrink-0' />
                    <div className='flex-1 flex-col gap-2'>
                        <Skeleton className='h-3 w-3/5' />
                        <Skeleton className='h-3 w-2/5' />
                    </div>
                    <Skeleton className='h-5 w-14 rounded-full shrink-0' />
                </div>
            ))}
        </div>
    );
}
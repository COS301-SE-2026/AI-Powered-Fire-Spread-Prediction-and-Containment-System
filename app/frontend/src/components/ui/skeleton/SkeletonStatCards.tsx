import { cx } from "@/lib/cx";
import { Skeleton } from "./Skeleton";

export function SkeletonStatCards({
    count = 4,
    className,
}: Readonly<{ count?: number; className?: string }>) {
    return (
        <div aria-hidden='true' className={cx('grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4', className)}>
            {Array.from({ length: count }, (_, i) => (
                <div
                    key={i}
                    className='rounded-2xl border border-carbon-stroke bg-carbon-side/30 p-4 flex flex-col gap-3'
                >
                    <Skeleton className='h-3 w-1/2' />
                    <Skeleton className='h-8 w-2/3' />
                    <Skeleton className='h-3 w-1/3' />
                </div>
            ))}
        </div>
    );
}
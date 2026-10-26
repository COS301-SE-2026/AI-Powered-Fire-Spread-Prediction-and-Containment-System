import { Skeleton } from './Skeleton';

export function SkeletonLegend() {
    return (
        <div aria-hidden='true' className='flex flex-wrap items-center gap-x-4 gap-y-1 px-1'>
            {[0, 1, 2, 3, 4].map((i) => (
                 <div key={i} className='flex items-center gap-1.5'>
                    <Skeleton className='size-3 rounded-sm' />
                    <Skeleton className='h-3 w-12' />
                 </div>
            ))}
        </div>
    );
}
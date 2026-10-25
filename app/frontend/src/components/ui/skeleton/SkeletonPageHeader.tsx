import { Skeleton } from './Skeleton';


export function SkeletonPageHeader() {
    return (
        <div aria-hidden='true' className='flex items-start justify-between gap-4 mb-4 md:mb-6'>
            <div className='flex flex-col gap-3 flex-1'>
                <Skeleton className='h-8 md:h-10 w-3/5 max-w-md' />
                <Skeleton className='h-4 w-4/5 max-w-md' />
            </div>
            <div className='flex gap-3 shrink-0'>
                <Skeleton className='size-8 rounded-full' />
                <Skeleton className='size-8 rounded-full' />
            </div>
        </div>
    );
}
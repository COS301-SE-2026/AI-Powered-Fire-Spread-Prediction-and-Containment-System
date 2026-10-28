import { Skeleton } from "./Skeleton";

export function SkeletonToolbar() {
    return (
        <div aria-hidden='true' className='flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-4'>
            <Skeleton className='h-10 w-full md:w-80 rounded-lg' />
            <Skeleton className='h-10 w-full md:w-80 rounded-lg' />
        </div>
    );
}
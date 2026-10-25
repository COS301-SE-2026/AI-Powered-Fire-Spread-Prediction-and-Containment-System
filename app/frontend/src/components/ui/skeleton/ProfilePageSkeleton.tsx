import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonPageHeader } from "./SkeletonPageHeader";
import { SkeletonTable } from "./SkeletonTable";
import { SkeletonCard } from "./SkeletonCard";

export function ProfilePageSkeleton({ label= 'Loading profile '}: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='p-3 md:p-6 flex flex-col w-full gap-4 md:gap-6'>
            <SkeletonPageHeader />
            <SkeletonCard className='flex-row! items-center gap-4'>
                <Skeleton className='size-16 rounded-full shrink-0' />
                <div className='flex-1 flex flex-col gap-2'>
                    <Skeleton className='h-5 w-48' />
                    <Skeleton className='h-3 w-64 max-w-full' />
                </div>
            </SkeletonCard>
            <SkeletonCard>
                <Skeleton className='h-4 w-40' />
                <div className='grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3'>
                    {Array.from({ length: 3 }, (_, i) => (
                        <Skeleton key={i} className='h-20 rounded-xl' />
                    ))}
                </div>
            </SkeletonCard>
            <SkeletonCard>
                <Skeleton className='h-4 w-36' />
                <SkeletonTable rows={3} cols={4} />
            </SkeletonCard>
        </SkeletonRegion>
    );
}
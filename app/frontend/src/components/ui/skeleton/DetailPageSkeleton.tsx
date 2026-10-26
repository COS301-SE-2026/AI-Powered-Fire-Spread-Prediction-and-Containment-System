import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonText } from "./SkeletonText";
import { SkeletonPageHeader } from "./SkeletonPageHeader";
import { SkeletonCard } from "./SkeletonCard";
import { SkeletonListBody } from "./SkeletonListBody";

export function DetailPageSkeleton({ label = 'Loading page' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label ={label} className='p-3 md:p-6 flex flex-col w-full gap-4'>
            <SkeletonPageHeader />
            <div className='grid grid-cols-1 xl:grid-cols-12 gap-4 md:gap-6'>
                <SkeletonCard className='xl:col-span-7 gap-4'>
                    <Skeleton className='h-5 w-48' />
                    <SkeletonText lines={4} />
                    <Skeleton className='h-48 w-full rounded-xl' />
                </SkeletonCard>
                <SkeletonCard className='xl:col-span-5 gap-4'>
                    <Skeleton className='h-5 w-36' />
                    <SkeletonListBody rows={3} />
                </SkeletonCard>
            </div>
        </SkeletonRegion>
    );
}
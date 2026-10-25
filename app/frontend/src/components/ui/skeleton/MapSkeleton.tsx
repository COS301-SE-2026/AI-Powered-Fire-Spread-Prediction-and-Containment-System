import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonPageHeader } from "./SkeletonPageHeader";
import { SkeletonCard } from "./SkeletonCard";
import { SkeletonMapBody } from "./SkeletonMapBody";
import { SkeletonListBody } from "./SkeletonListBody";

export function MapPageSkeleton({ label = 'Loading map page' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='p-2 md:p-4 flex flex-col w-full gap-3 md:gap-4'>
            <MapPageSkeleton />
            <div className='grid grid-cols-1 xl:grid-cols-12 gap-3 md:gap-4'>
                <div className='xl:col-span-8 h-96 sm:h-104 md:h-136'>
                    <SkeletonMapBody />
                </div>
                <SkeletonCard className='xl:col-span-4'>
                    <Skeleton className='h-4 w-36' />
                    <SkeletonListBody rows={4} />
                </SkeletonCard>
            </div>
        </SkeletonRegion>
    );
}
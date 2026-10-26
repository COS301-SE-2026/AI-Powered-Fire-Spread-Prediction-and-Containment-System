import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonPageHeader } from "./SkeletonPageHeader";
import { SkeletonCard } from "./SkeletonCard";
import { SkeletonMapBody } from "./SkeletonMapBody";

export function FormPageSkeleton({ label = 'Loading form' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='p-3 md:p-6 flex-col w-full gap-4'>
             <SkeletonPageHeader />
             <div className='grid grid-cols-1 xl:grid-cols-2 gap-4 md:gap-6'>
                <SkeletonCard className='gap-5'>
                    {Array.from({ length: 4 }, (_,i) => (
                        <div key={i} className='flex flex-col gap-2'>
                            <Skeleton className='h-3 w-24' />
                            <Skeleton className='h-10 w-full rounded-lg' />
                        </div>
                    ))}
                </SkeletonCard>
                <div className='min-h-72 md:min-h-96'>
                    <SkeletonMapBody />
                </div>
             </div>
        </SkeletonRegion>
    );
}
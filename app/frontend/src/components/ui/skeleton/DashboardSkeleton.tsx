import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonPageHeader } from "./SkeletonPageHeader";
import { SkeletonStatCards } from "./SkeletonStatCards";
import { SkeletonCard } from "./SkeletonCard";
import { SkeletonListBody } from "./SkeletonListBody";

export function DashboardSkeleton({ label = 'Loading dashboard' }: Readonly<{ label?: string}>) {
    return (
        <SkeletonRegion label={label} className='p-3 md:p-6 flex flex-col w-full gap-4 md:gap-6'>
            <SkeletonPageHeader />
            <SkeletonStatCards count={4} />
            <div className='grid grid-cols-1 xl:grid-cols-12 gap-4 md:gap-6'>
                <Skeleton className='h4 w-40' />
                <div className='flex-1 flex items-end gap-2 md:gap-4 pt-4'>
                    {[40, 65, 50, 80, 55, 90, 70].map((h, i) => (
                        <div 
                            key={i}
                            aria-hidden='true'
                            style={{ height: `${h}%` }}
                            className='flex-1 flex items-end gap-2 md:gap-4 pt-4'
                        />
                    ))}
                </div>
            <SkeletonCard/>
            <SkeletonCard className='xl:col-span-4 min-h-72'>
                <Skeleton className='h-4 w-32' />
                <SkeletonListBody rows={4} />
            </SkeletonCard>
            </div>
        </SkeletonRegion>
    );
}

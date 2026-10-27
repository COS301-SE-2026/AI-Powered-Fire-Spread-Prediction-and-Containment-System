import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { SkeletonMapBody } from './SkeletonMapBody';
import { SkeletonLegend } from './SkeletonLegend';
import { SkeletonSidePanel } from './SkeletonSidePanel';
import { Skeleton } from './Skeleton';

export function FirefighterDashboardSkeleton({
    label = 'Loading dashboard',
}: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1 p-2 md:p-6'>
            <SkeletonPageHeader />

            <div className='grid grid-cols1 xl:grid-cols-12 gap-3 md:gap-4 xl:grid-rows-1'>
                {/* left column */}
                <div className='xl:col-span-8 flex flex-col gap-3 md:gap-4'>
                    <div className='h-96 sm:h-104 md:h-136'>
                        <SkeletonMapBody />
                    </div>
                    <SkeletonLegend />

                    <div aria-hidden='true' className='grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-2 shrink-0'>
                        <div className='flex flex-col gap-3'>
                            <Skeleton className='h-5 w-44' />
                            <div className='grid grid-cols-2 grid-rows-2 gap-3'>
                                {[0, 1, 2, 3].map((i) => (
                                    <Skeleton key={i} className='h-24 rounded-xl' />
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
                {/* right colunm */}

                <div className='xl:col-span-4 flex flex-col gap-3'>
                    <SkeletonSidePanel rows={3} panelClassName='ax-h-64' />
                    <SkeletonSidePanel rows={4} className='flex-1' />
                </div>
            </div>
        </SkeletonRegion>
    );
}


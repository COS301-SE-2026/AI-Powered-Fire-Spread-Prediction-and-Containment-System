import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { SkeletonMapBody } from './SkeletonMapBody';
import { SkeletonEnvironentBar } from './SkeletonEnvironmentBar';
import { SkeletonLegend } from './SkeletonLegend';
import { SkeletonSidePanel } from './SkeletonSidePanel';
import { Skeleton } from './Skeleton';

export function AdminLiveMapSkeleton({ label ='Loading live map' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1 p2'>
            <SkeletonPageHeader />

            <div className='grid grid-cols-1 xl:grid-cols-12  gap-6'>
                <div className='xl:col-span-8 flex flex-col gap-6'>
                    {/* water / resources toggles */}
                    <div aria-hidden='true' className='flex justify-end gap-4'>
                        <Skeleton className='h-9 w-36 rounded-full' />
                        <Skeleton className='h-9 w-44 rounded-full' />
                    </div>
                    <div className='relative w-full h-96 sm:h-104 lg:h-140'>
                        <SkeletonMapBody />
                        <SkeletonEnvironentBar />
                    </div>
                    <SkeletonLegend />
                </div>

                <div className='xl:col-span-4 flex flex-col gap-3 xl:h-150'>
                    <SkeletonSidePanel rows={3} panelClassName='ax-h-130' />
                    <SkeletonSidePanel rows={3} className='xl:flex-1 xl:min-h-0' />
                </div>
            </div>
        </SkeletonRegion>
    );
}

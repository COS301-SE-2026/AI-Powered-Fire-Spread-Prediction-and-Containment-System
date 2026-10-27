import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { SkeletonMapBody } from './SkeletonMapBody';
import { SkeletonEnvironentBar } from './SkeletonEnvironmentBar';
import { SkeletonSidePanel } from './SkeletonSidePanel';

export function UserLiveMapSkeleton({ label = 'Loading live map' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1 px-2 py-2'>
            <SkeletonPageHeader />

            <div className='grid grid-cols-1 xl:grid-cols-12 gap-3 lg:gap-6'>
                <div className='xl:col-span-8 flex flex-col gap-3'>
                    <div className='relative w-full h-120 sm:h-130 lg:h-[80vh]'>
                        <SkeletonMapBody />
                        <SkeletonEnvironentBar />
                    </div>
                </div>
                <SkeletonSidePanel rows={5} className='xl:col-span-4' panelClassName='max-h-132' />
            </div>
        </SkeletonRegion>
    );
}
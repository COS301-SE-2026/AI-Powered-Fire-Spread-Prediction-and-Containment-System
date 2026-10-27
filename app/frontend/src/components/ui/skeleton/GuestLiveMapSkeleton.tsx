import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { SkeletonMapBody } from './SkeletonMapBody';
import { SkeletonEnvironentBar } from './SkeletonEnvironmentBar';
import { SkeletonSidePanel } from './SkeletonSidePanel';

export function GuestLiveMapSkeleton({ label = 'Loading live map' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1 px-1 py-1 lg:px-6 lg:py-6'>
            <SkeletonPageHeader showIcons={false} />

            <div className='grid grid-cols-1 xl:grid-cols-12 gap-3 lg:gap-6'>
                <div className='xl:col-span-8 flex flex-col gap-3 lg:gap-6'>
                    <div className='relative w-full h-125 sm:h-104 md:h-120 lg:h-[80vh]'>
                        <SkeletonMapBody />
                        <SkeletonEnvironentBar />
                    </div>
                </div>
                <SkeletonSidePanel rows={5} className='xl:col-span-4 h-full' panelClassName='ax-h-130' />
            </div>
        </SkeletonRegion>
    );
}


import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { SkeletonMapBody } from './SkeletonMapBody';
import { SkeletonListBody } from './SkeletonListBody';
import { Skeleton } from './Skeleton';


export function SimulationPageSkeleton({ label = 'Loading siulation' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='p-2 landscape:p-2 flex flex-col flex-1 w-full gap-y-3 landscape:gap-y-2'>
            <SkeletonPageHeader />


            <div className='flex flex-col lg:flex-row gap-4 in-w-0'>
                {/* left: map + controls */}
                <div className='basis-full lg:basis-3/4 flex flex-col gap-4 in-w-0'>
                    <div className='h-[50vh] landscape:h-[60vh]'>
                        <SkeletonMapBody />
                    </div>

                    <div aria-hidden='true' className='flex flex-col lg:flex-row gap-3 items-stretch'>
                        <div className='flex flex-col gap-3 shrink-0 w-full lg:w-80'>
                            <Skeleton className='h-10 w-full rounded-xl' />
                            <Skeleton className='h-10 w-full rounded-xl' />
                            <div className='flex gap-2'>
                                <Skeleton className='h-10 flex-1 rounded-xl' />
                                <Skeleton className='h-10 flex-1 rounded-xl' />
                            </div>
                            <div className='flex gap-2'>
                                <Skeleton className='h-10 flex-1 rounded-xl' />
                                <Skeleton className='h-10 flex-1 rounded-xl' />
                            </div>
                        </div>
                        <div className='flex-1 rounded-2xl border border-carbon-stroke p-4 flex flex-col gap-4'>
                            <Skeleton className='h-4 w-32' />
                            <Skeleton className='h-3 w-full rounded-full' />
                            <Skeleton className='h-10 w-full rounded-lg' />
                        </div>
                    </div>
                </div>

                {/* right: results */}
                <div
                    aria-hidden='true'
                    className='basis-full lg:basis-1/4 rounded-2xl border border-carbon-stroke p-3 flex flex-col gap-3 ax-h-[40vh] lg:max-h-none overflow-hidden'
                >
                    <Skeleton className='h-4 w-28'/>
                    <SkeletonListBody rows={4} />
                </div>
            </div>
        </SkeletonRegion>
    );
}
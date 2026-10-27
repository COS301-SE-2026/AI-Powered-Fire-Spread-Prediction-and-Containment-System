import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { SkeletonMapBody } from './SkeletonMapBody';
import { Skeleton } from './Skeleton';

export function ReportDetailSkeleton({ label = 'Loading report' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='p-2 flex flex-col flex-1 w-full'>
            <Skeleton className='size-8 rounded-lg shrink-0' />
            <SkeletonPageHeader />

            <div className='grid grid-cols-1 lg:grid-cols-12 gap-2 flex-1'>
                {/* left */}
                <div className='lg:col-span-6 flex flex-col gap-3'>
                    <div className='flex-1 w-full in-h-64'>
                        <SkeletonMapBody />
                    </div>
                    <div aria-hidden='true' className='rounded-2xl border border-carbon-stroke p-4 flex-col gap-3'>
                        <Skeleton className='h-5 w-32' />
                        <div className='grid grid-cols-2 gap-3'>
                            {[0, 1, 2, 3].map((i) => (
                            <div key={i} className='flex flex-col gap-2'>
                                <Skeleton className='h-3 w-20' />
                                <Skeleton className='h-4 w-32' />
                            </div>
                        ))}
                        </div>
                    </div>
                </div>
            

                {/* right */}
                <div aria-hidden='true' className='lg:col-span-6 flex flex-col gap-2'>
                    <Skeleton className='h-64 w-full rounded-2xl' />
                    <div className='rounded-2xl border border-carbon-stroke p-4 flex flex-col gap-3'>
                        <Skeleton className='h-5 w-28' />
                        <Skeleton className='h-3 w-full' />
                        <Skeleton className='h-3 w-5/6' />
                        <Skeleton className='h-3 2-2/3' />
                    </div>
                    <div className='rounded-2xl border border-carbon-stroke p-4 flex flex-col gap-3'>
                        <Skeleton className='h-10 flex-1 rounded-lg' />
                        <Skeleton className='h-10 flex-1 rounded-lg' />
                    </div>
                </div>
            </div>
        </SkeletonRegion>
    );
}
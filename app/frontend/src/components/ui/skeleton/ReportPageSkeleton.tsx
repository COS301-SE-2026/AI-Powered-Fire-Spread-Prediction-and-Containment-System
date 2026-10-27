import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { Skeleton } from './Skeleton';

export function ReportPageSkeleton({ label = 'Loading form' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1 p-2'>
            <SkeletonPageHeader showSubtitle={false} />
            {/* step indicator */}
            <div aria-hidden='true' className='flex flex-col flex-1 p-2'>
                {['w-44', 'w-56', 'w-40'].map((w) => (
                    <div key={w} className='flex items-center gap-2'>
                        <Skeleton className='size-6 rounded-full' />
                        <Skeleton className={`h-4 ${w}`} />
                    </div>
                ))}
            </div>

            <div className='grid grid-cols-1 xl:grid-cols-12 gap-4 xl:grid-rows-1 mt-4'>
                {/* map card */}
                <div className='xl:col-span-8 flex flex-col gap-4'>
                    <div
                        aria-hidden='true'
                        className='rounded-lg border border-carbon-stroke flex flex-col overflow-hidden h-96 sm:h-104 lg:h-132 xl:h-150'
                    >
                        <div className='p-4 border-b border-carbon-card'>
                            <Skeleton className='h-6 w-28' />
                        </div>
                        <Skeleton className='flex-1 w-full rounded-none' />
                    </div>
                </div>

                {/* form + status */}
                <div aria-hidden='true' className='xl:col-span-4 flex flex-col gap-3'>
                    <div className='rounded-lg border border-carbon-stroke p-3 flex flex-col gap-4'>
                        {[0, 1, 2].map((i) => (
                            <div key={i} className='flex flex-col gap-2'>
                                <Skeleton className='h-3 w-24' />
                                <Skeleton className='h-10 w-full rounded-lg' />
                            </div>
                        ))}
                        <Skeleton className='h-11 w-full rounded-lg' />
                    </div>
                    <div className='rounded-lg border border-carbon-stroke p-3 flex flex-col gap-3'>
                        <Skeleton className='h-4 w-28' />
                        <Skeleton className='h-12 w-full rounded-lg' />
                    </div>
                </div>
            </div>
        </SkeletonRegion>
    );
}
import { SkeletonRegion } from './SkeletonRegion';
import { SkeletonPageHeader } from './SkeletonPageHeader';
import { Skeleton } from './Skeleton';

export function HelpPageSkeleton({ label = 'Loading Help' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1'>
            <div className='flex flex-col p-6'>
                <SkeletonPageHeader />
            </div>

            <div aria-hidden='true' className='flex flex-col p-6 gap-3'>
                {/* two tutorial accordians */}
                {[0, 1].map((i) => (
                    <div key={i} className='border border-carbon-card rounded-lg p-4 flex ites-center gap-3'>
                        <Skeleton className='size-10 rounded-lg shrink-0' />
                        <div className='flex flex-col gap-2'>
                            <Skeleton className='h-4 w-36' />
                            <Skeleton className='h-3 w-24' />
                        </div>
                    </div>
                ))}
                {/* help center card */}
                <div className='flex items-center gap-4 p-5 rounded-xl border border-carbon-stroke'>
                    <Skeleton className='size-10 rounded-lg shrink-0' />
                    <div className='flex flex-col gap-2'>
                        <Skeleton className='h-4 w-28' />
                        <Skeleton className='h-3 w-44'  />
                    </div>
                </div>
            </div>

            {/* FAQs */}
            <div aria-hidden='true' className='px-6'>
                <Skeleton className='h-7 w-20 mb-4' />
                <div className='space-y-3'>
                    {Array.from({ length: 11 }, (_, i) => (
                        <div key={i} className='border border-white/5 rounded-d px-3 py-3 flex ites-center justify-between gap-4'>
                            <Skeleton className='h-4 w-3/5' />
                            <Skeleton className='size-4 shrink-0' />
                        </div>
                    ))}
                </div>
            </div>
        </SkeletonRegion>
    );
}
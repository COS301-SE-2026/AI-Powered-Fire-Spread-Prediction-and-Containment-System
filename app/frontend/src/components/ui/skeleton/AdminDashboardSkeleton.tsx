import { SkeletonRegion } from "./SkeletonRegion";
import { SkeletonPageHeader } from "./SkeletonPageHeader";
import { Skeleton } from "./Skeleton";

export function AdminDashboardSkeleton({ label = 'Loading dashboard' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='w-full space-y-6'>
            <SkeletonPageHeader />

            {/* metric card */}
            <section aria-hidden='true' className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'>
                {[0, 1, 2, 3].map((i) => (
                    <div key={i} className='border border-carbon-stroke p-5 rounded-xl flex flex-col gap-3'>
                        <Skeleton className='h-4 w-28' />
                        <Skeleton className='h-9 w-16' />
                    </div>
                ))}
            </section>

            <div aria-hidden='true' className='grid grid-cols-1  lg:grid-cols-2 gap-2 w-full p-2'>
                {/* recent activity */}
                <section className='border border-carbon-stroke rounded p-6 flex flex-col gap-4'>
                    <Skeleton className='h-5 w-40' />
                    <div className='divide-y divide-carbon-stroke/60'>
                        {[0, 1, 2, 3, 4, 5].map((i) => (
                            <div key={i} className='py-3 px-2 flex items-start justify-between gap-4'>
                                <Skeleton className='h-4 w-3/5' />
                                <Skeleton className='h-4 w-16' />
                            </div>
                        ))}
                    </div>
                </section>

                {/* incidents this week */}
                <section className='border border-carbon-stroke rounded p-6 flex flex-col justify-between min-h-75'>
                    <div className='flex flex-col gap-6'>
                        <Skeleton className='h-5 w-44' />
                        <div className='flex justify-between items-end h-48 pt-4 px-4 rounded border border-carbon-stroke'>
                            {[40, 65, 50, 80, 55, 90, 70].map((h, i) => (
                                <div key={i} className='flex flex-col items-center flex-1 mx-1.5 h-full justify-end gap-2'>
                                    <div style={{ height: `${h}%` }} className='skeleton w-full rounded-t-sm' />
                                    <Skeleton className='h-3 w-8' />
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className='mt-4 pt-4 border-t border-carbon-stroke flex justify-between'>
                        <Skeleton className='h-4 w-36' />
                        <Skeleton className='h-4 w-44' />
                    </div>
                </section>
            </div>
        </SkeletonRegion>
    );
}
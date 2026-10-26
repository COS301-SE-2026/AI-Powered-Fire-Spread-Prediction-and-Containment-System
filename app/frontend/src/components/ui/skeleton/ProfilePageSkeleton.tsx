import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonTable } from "./SkeletonTable";
import { SkeletonCard } from "./SkeletonCard";
import { SkeletonToolbar } from "./SkeletonToolbar"

export function ProfilePageSkeleton({ label= 'Loading profile '}: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='flex flex-col flex-1 p-6'>
            {/* avatar + name */}
            <div aria-hidden='true' className='flex items-center gap-8 mt-6 mb-8 pb-8'>
                <Skeleton className='size-20 rounded-full shrink-0' />
                <div className='flex flex-col gap-3'>
                    <Skeleton className='h-8 w-56' />
                    <Skeleton className='h-5 w-24' />
                </div>
            </div>

            {/* account info + role requests */}
            <div aria-hidden='true' className='grid grid-cols-1 lg:grid-cols-2 gap-6 b-6'>
                <div className='rounded-2xl border border-carbon-stroke p-10 flex flex-col gap-6'>
                    <Skeleton className='h-6 w-36' />
                    <div className='grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-8'>
                        {[0, 1, 2, 3].map((i) => (
                            <div key={i} className='flex flex-col gap-2'>
                                <Skeleton className='h-3 w-20' />
                                <Skeleton className='h-5 w-40' />
                            </div>
                        ))}
                    </div>
                </div>
                <div className='rounded-2xl border border-carbon-stroke p-10 flex flex-col gap-6'>
                        <Skeleton className='h-6 w-36' />
                        {[0, 1, 2].map((i) => (
                            <div key={i} className='flex items-center gap-3'>
                                <Skeleton className='size-10 rounded-lg shrink-0' />
                                <Skeleton className='h-5 flex-1' />
                                <Skeleton className='h-5 w-40' />
                            </div>
                        ))}
                </div>
            </div>

            {/* saved locations */}
            <div aria-hidden='true' className='rounded-2xl border border-carbon-stroke p-4 mb-6 flex flex-col gap-4'>
                <Skeleton className='h-6 w-44' />
                <div className='grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4'>
                    {[0, 1, 2].map((i) => (
                        <Skeleton key={i} className='h-24 rounded-xl' />
                    ))}
                </div>
            </div>

            {/* my reports + resources table */}
            {['reports', 'resources'].map((name) => (
                <div
                    key={name}
                    aria-hidden='true'
                    className='w-full rounded-2xl border border-carbon-stroke p-4 mb-6 flex flex-col'
                >
                    <Skeleton className='h-6 w-40 mb-3' />
                    <SkeletonToolbar />
                    <SkeletonTable rows={3} cols={5} />
                </div>
            ))}
        </SkeletonRegion>
    );
}
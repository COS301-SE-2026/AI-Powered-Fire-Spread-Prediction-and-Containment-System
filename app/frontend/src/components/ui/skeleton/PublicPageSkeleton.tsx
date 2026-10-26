import { SkeletonRegion } from "./SkeletonRegion";
import { Skeleton } from "./Skeleton";
import { SkeletonCard } from "./SkeletonCard";

export function PublicPageSkeleton({ label = 'Loading page' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion
            label={label}
            className='min-h-screen flex flex-col items-center justify-center gap-6 p-4'
        >
            <Skeleton className='h-24 w-60 rounded-xl' />
            <SkeletonCard className='w-full max-w-md gap-5 p-6'>
                <Skeleton className='h-6 w-40 self-center' />
                {Array.from({ length: 2 }, (_, i) => (
                    <div key={i} className='flex flex-col gap-2'>
                        <Skeleton className='h-3 w-20' />
                        <Skeleton className='h-10 w-full rounded-lg' />
                    </div>
                ))}
                <Skeleton className='h-11 w-full rounded-lg' />
            </SkeletonCard>
        </SkeletonRegion>
    );
}
import { SkeletonRegion } from './SkeletonRegion';
import { Skeleton } from './Skeleton';
import { SkeletonCard } from './SkeletonCard';

export function RegistrationPageSkeleton({ label ='Loading page' }: Readonly<{ label?: string }>) {
    return (
        <SkeletonRegion label={label} className='min-h-screen flex flex-col items-center justify-center gap-6 p-4'>
            <Skeleton className='h-24 w-60 rounded-xl' />
            <SkeletonCard className='w-full max-w-3xl p-6 gap-4'>
                <Skeleton className='h-6 w-40 self-center' />
                <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
                    {/* name, surname*/}
                    {[0, 1].map((i) => (
                        <div key={i} className='flex flex-col gap-2'>
                            <Skeleton className='h-3 w-16' />
                            <Skeleton className='h-10 w-full rounded-d' />
                        </div>
                    ))}
                    {/* email, ID number */}
                    {[0, 1].map((i) => (
                        <div key={i} className='md:col-span-2 flex flex-col gap-2'>
                            <Skeleton className='h-3 w-24' />
                            <Skeleton className='h-10 w-full rounded-md' />
                        </div>
                    ))}
                    {/* password, confirm password */}
                    {[0, 1].map((i) => (
                        <div key={i} className='flex flex-col gap-2'>
                            <Skeleton className='h-3 w-12' />
                            <Skeleton className='h-10 w-full rounded-md' />
                        </div>
                    ))}
                    {/* role */}
                    <div className='md:col-span-2 flex flex-col gap-2'>
                        <Skeleton className='h-3 w-12' />
                        <Skeleton className='h-10 w-full rounded-md' />
                    </div>
                    {/* buttons */}
                    <Skeleton className='md:col-span-2 h-11 w-full rounded-md mt-2' />
                    <Skeleton className='md:col-span-2 h-10 w-full rounded-d' />
                </div>
            </SkeletonCard>
        </SkeletonRegion>
    );
}
import { Skeleton } from './Skeleton';

export function SkeletonEnvironentBar() {
    return (
        <div
            aria-hidden='true'
            className='absolute bottom-0 inset-x-0 z-10 bg-carbon-bg/70 border-t border-carbon-card p-2'
        >
            <div className='grid grid-cols-2 md:grid-cols-4 gap-1.5 sm:gap-2'>
                {[0, 1, 2, 3,].map((i) => (
                    <Skeleton key={i} className='h-14 rounded-xl' />
                ))}
            </div>
        </div>
    );
}
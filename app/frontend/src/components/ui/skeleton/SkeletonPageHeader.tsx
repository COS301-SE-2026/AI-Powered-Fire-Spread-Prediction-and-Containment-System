import { Skeleton } from './Skeleton';


export function SkeletonPageHeader({
    showSubtitle = true,
    showIcons = true,
}: Readonly<{ showSubtitle?: boolean; showIcons?: boolean }>) {
    return (
        <header aria-hidden='true' className='mb-4 mt-2'>
            <div className='flex items-start justify-between gap-1'>
                <div className='min-w-0 flex flex-col gap-2'>
                    <Skeleton className='h-9 w-64 ax-w-full' />
                    {showSubtitle && <Skeleton className='h-5 w-80 max-w-full' />}
                </div>
                {showIcons && (
                    <div className='flex ites-center gap-1'>
                        <Skeleton className='size-12 rounded-full' />
                        <Skeleton className='size-12 rounded-full' />
                    </div>
                )}
            </div>
        </header>
    );
}
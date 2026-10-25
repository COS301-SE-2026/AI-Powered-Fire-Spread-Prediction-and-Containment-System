import { cx } from '../../../lib/cx';
import { Skeleton } from './Skeleton';

export function SkeletonTable({
    rows = 6,
    cols = 5,
    className,
}: Readonly<{ rows?: number; cols?: number; className?: string }>) {
    return (
        <div
            aria-hidden='true'
            className={cx('w-full rounded-2xl border border-carbon-stroke overflow-hidden bg-carbon-side/30', className)}
        >
            {/* header row */}
            <div className='flex gap-4 px-4 py-3 border-b border-carbon-stroke bg-white/3'>
                {Array.from({ length: cols }, (_, c) => (
                    <Skeleton
                        key={c}
                        className={cx('h-3 flex-1', c > 1 && 'hidden md:block', c > 3 && 'hidden lg:block')}
                    />
                ))}
            </div>
            {/* body rows */}
            {Array.from({ length: rows }, (_, r) => (
                <div
                    key={r}
                    className='flex items-center gap-4 px-4 py-4 border-b border-carbon-stroke/60 last:border-b-0'
                >
                    {Array.from({ length: cols }, (_, c) => (
                        <Skeleton
                            key={c}
                            className={cx('h-4 flex-1', c === cols - 1 && 'max-w-24 rounded-full', c > 1 && 'hidden md:block', c > 3 && 'hidden lg:block')}
                        />
                    ))}
                </div>
            ))}
        </div>
    );
}
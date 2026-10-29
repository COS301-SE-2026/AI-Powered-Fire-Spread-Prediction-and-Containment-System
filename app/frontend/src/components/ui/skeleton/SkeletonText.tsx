import { cx } from '../../../lib/cx';
import { Skeleton } from './Skeleton';

export function SkeletonText({
    lines = 3,
    className,
}: Readonly<{ lines?: number; className?: string}>) {
    return (
        <div aria-hidden='true' className={cx('flex flex-col gap-2', className)}>
            {Array.from({ length: lines }, (_, i) => (
                <Skeleton key={i} className={cx('h-3', i === lines -1 && lines > 1 ? 'w-2/3' : 'w-full')} />
            ))}
        </div>
    );
}
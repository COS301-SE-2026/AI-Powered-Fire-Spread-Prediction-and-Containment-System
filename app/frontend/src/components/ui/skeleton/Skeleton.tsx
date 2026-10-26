import { cx } from '../../../lib/cx';

export function Skeleton({ className = undefined }: Readonly<{ className?: string }>) {
    return (
        <div  
            aria-hidden ='true'
            className={cx('skeleton rounded-md', className)}
        />
    );
}
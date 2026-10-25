import { Skeleton } from "./Skeleton"
import { SkeletonRegion } from "./SkeletonRegion";
import { SkeletonTable } from "./SkeletonTable";

export function TableSkeleton({
    rows,
    cols,
    label = 'loading',
    className,
}: Readonly<{ rows?: number; cols?: number; label?: string; className?: string}>) {
    return (
        <SkeletonRegion label={label} className={className}>
            <SkeletonTable rows={rows} cols={cols} />
        </SkeletonRegion>
    );
}
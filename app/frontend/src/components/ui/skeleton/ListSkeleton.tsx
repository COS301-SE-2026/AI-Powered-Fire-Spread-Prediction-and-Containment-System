import { SkeletonRegion } from "./SkeletonRegion";
import { SkeletonListBody } from "./SkeletonListBody";

export function ListSkeleton({
    rows,
    label = 'Loading list',
    className,
}: Readonly<{ rows?: number; label?: string; className?: string }>) {
    return (
        <SkeletonRegion label={label} className={className}>
            <SkeletonListBody rows={rows} />
        </SkeletonRegion>
    );
}
import { SkeletonRegion } from "./SkeletonRegion";
import { SkeletonStatCards } from "./SkeletonStatCards";

export function CardSkeleton({
    count = 4,
    label = 'Loading',
    className,
}: Readonly<{ count?: number; label?: string; className?: string }>) {
    return (
        <SkeletonRegion label={label} className={className}>
            <SkeletonStatCards count={count} />
        </SkeletonRegion>
    );
}
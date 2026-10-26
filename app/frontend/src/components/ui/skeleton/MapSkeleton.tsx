import { cx } from "@/lib/cx";
import { SkeletonRegion } from "./SkeletonRegion";
import { SkeletonMapBody } from "./SkeletonMapBody";

export function MapSkeleton({
    label = 'Initializing Map',
    className,
}: Readonly<{ label?: string; className?: string }>) {
    return (
        <SkeletonRegion label='Loading map' className={cx('flex-1 w-full h-full', className)}> 
            <SkeletonMapBody label={label} className='rounded-none border-0' />
        </SkeletonRegion>
    );
}
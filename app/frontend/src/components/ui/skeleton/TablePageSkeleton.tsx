 import { SkeletonRegion } from "./SkeletonRegion";
 import { SkeletonPageHeader } from "./SkeletonPageHeader";
 import { SkeletonToolbar } from "./SkeletonToolbar";
 import { SkeletonTable } from "./SkeletonTable";

 export function TablePageSkeleton({
    label = 'Loading page',
    rows = 8,
    showHeader = true,
 }: Readonly<{ label?: string; rows?: number; showHeader?: boolean }>) {
    return (
        <SkeletonRegion label={label} className='p-3 md:p-6 flex flex-col w-full'>
            {showHeader && <SkeletonPageHeader />}
            <SkeletonToolbar />
            <SkeletonTable />
        </SkeletonRegion>
    );
 }
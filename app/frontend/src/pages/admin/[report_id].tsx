import { useRouter } from 'next/router';
import { SideBarLayout } from '../../components/demoSidebar';

export default function ViewPage() {
    const router = useRouter();
    const { report_id } = router.query;

    return (
        <SideBarLayout>
            <div className="p-6 flex flex-col h-full w-full">
                <div className='flex items-center gap-2 mb-6 text-sm text-neutral/50'>
                    <header className="mb-6">
                        <h1 className='uppercase'>Report {report_id}</h1>
                        <p className='text-text-muted'>Viewing fire report details</p>
                        <button onClick={() => router.back()} className="mt-3 flex items-center gap-1 px-3 py-1 rounded-lg border border-carbon-card text-neutral/50 hover:bg-smoke-hover hover:text-neutral transition-colors text-xs font-semibold">Back</button>
                    </header>
                </div>

                {/* 2 cols*/}
                <div className='grid grid-cols-1 xl:grid-cols-12 gap-4'>
                    {/*Left*/}
                    <div className='xl:col-span-7 flex flex-col gap-4'>

                    </div>
                    {/*Right*/}
                    <div className='xl:col-span-5 flex flex-col gap-4'>

                    </div>
                </div>
            
            </div>
        </SideBarLayout>
    );
}
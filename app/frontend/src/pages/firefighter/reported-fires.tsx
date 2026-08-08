import React, { useState, useEffect } from 'react';
import { Report, ReportStatus } from "../../types/firefighter-dashboard";
import { FirefighterSideBar } from '../../components/firefighter/firefighterSidebar';
import { ReportsTable } from '../../components/firefighter/reportsTable';
import { StatusTableFilter } from '../../components/firefighter/reportsFilter';
import { TableSearchBar } from '../../components/firefighter/searchbar';

function useDebounce(val: string, delayMs: number){
    const [debounced, setDebounced] = useState(val)

    useEffect(() => {
        const clock = setTimeout(() => {
            setDebounced(val)
        }, delayMs);

        return () => clearTimeout(clock);
    }, [val, delayMs])

    return debounced
}

export default function ReportTable() {
    const [request, setRequest] = useState<Report[]>([]);
    const [statusFilter, setStatusFilter] = useState<'all' | ReportStatus>('all');
    const [searchKey, setSearchKey] = useState("");

    const debouncedSearch = useDebounce(searchKey, 600); // this ensures that search only happens when the user stops typing for 300 ms this prevents multiple requests for each letter typed

    // call for search in the table
    useEffect(() => {
        const fetchRequest = async() => {
            const url = debouncedSearch ? `/api/firefighter/reported-fires/search?key=${encodeURIComponent(debouncedSearch)}` : `/api/firefighter/reported-fires`

            try{
                const resp = await fetch(url);
                if(!resp.ok){
                    if(resp.status == 404) {
                        setRequest([]);
                    }else{
                        console.warn("API unavailiable")
                        setRequest([]);
                    }

                    return;
                }
                const data = await resp.json();
                setRequest(data.data ?? []);

            } catch(error){
                    console.error("failed to find value requested", error)
                    setRequest([]);
            }
        };
            fetchRequest();
    }, [debouncedSearch]);


    return (
        <FirefighterSideBar>
            <div className="p-4 flex flex-col h-full w-full gap-y-3">
                            <header className="mb-6">
                                <h1 className="text-page-title font-display font-bold tracking-wider text-text-primary uppercase">Reported Fires</h1>
                                <p className="font-body text-body text-text-primary/50">View the reported fires</p>
                            </header>
                            {/* Header + filter + search */}
                            <div className="flex justify-between items-center">
                                    <StatusTableFilter filter={statusFilter} onChange={setStatusFilter}/>

                                    <TableSearchBar value={searchKey} onChange={setSearchKey}/>
                            </div>

                            {/* table */}
                            <ReportsTable requests={request} filter={statusFilter} onView={(req) => console.log(req)}/>
                        </div>
        </FirefighterSideBar>
    )
}
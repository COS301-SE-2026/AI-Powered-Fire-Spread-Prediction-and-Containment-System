import React, { useState } from 'react';
import { Report, ReportStatus } from "../../types/firefighter";
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportsTable } from '../../components/firefighter/reportsTable';
import { StatusTableFilter } from '../../components/firefighter/reportsFilter';
import { TableSearchBar } from '../../components/firefighter/searchbar';

const mockRequests: Report[] = [
  { Ref: "FIR-001", Location: "Johannesburg", Status: "pending", Size: 120, Reported: "2026-06-18", Reporter: "John Doe" },
  { Ref: "FIR-002", Location: "Pretoria", Status: "verified", Size: 85, Reported: "2026-06-17", Reporter: "Sarah Smith" },
  { Ref: "FIR-003", Location: "Cape Town", Status: "rejected", Size: 45, Reported: "2026-06-16", Reporter: "Michael Brown" },
  { Ref: "FIR-004", Location: "Durban", Status: "pending", Size: 210, Reported: "2026-06-15", Reporter: "Emily Johnson" },
  { Ref: "FIR-005", Location: "Polokwane", Status: "verified", Size: 95, Reported: "2026-06-14", Reporter: "David Wilson" },
  { Ref: "FIR-006", Location: "Nelspruit", Status: "pending", Size: 160, Reported: "2026-06-13", Reporter: "Lisa Anderson" },
  { Ref: "FIR-007", Location: "Bloemfontein", Status: "verified", Size: 130, Reported: "2026-06-12", Reporter: "Chris Taylor" },
  { Ref: "FIR-008", Location: "Kimberley", Status: "rejected", Size: 70, Reported: "2026-06-11", Reporter: "Jessica Thomas" },
  { Ref: "FIR-009", Location: "Rustenburg", Status: "pending", Size: 180, Reported: "2026-06-10", Reporter: "Daniel White" },
  { Ref: "FIR-010", Location: "George", Status: "verified", Size: 110, Reported: "2026-06-09", Reporter: "Amanda Martin" },
  { Ref: "FIR-011", Location: "Pietermaritzburg", Status: "pending", Size: 250, Reported: "2026-06-08", Reporter: "Ryan Clark" },
  { Ref: "FIR-012", Location: "East London", Status: "verified", Size: 140, Reported: "2026-06-07", Reporter: "Olivia Lewis" },
  { Ref: "FIR-013", Location: "Mahikeng", Status: "rejected", Size: 55, Reported: "2026-06-06", Reporter: "Ethan Walker" },
  { Ref: "FIR-014", Location: "Welkom", Status: "pending", Size: 320, Reported: "2026-06-05", Reporter: "Sophia Hall" },
  { Ref: "FIR-015", Location: "Mthatha", Status: "verified", Size: 75, Reported: "2026-06-04", Reporter: "James Allen" },
  { Ref: "FIR-016", Location: "Upington", Status: "pending", Size: 190, Reported: "2026-06-03", Reporter: "Grace Young" },
  { Ref: "FIR-017", Location: "Tzaneen", Status: "verified", Size: 100, Reported: "2026-06-02", Reporter: "Benjamin King" },
  { Ref: "FIR-018", Location: "Middelburg", Status: "rejected", Size: 40, Reported: "2026-06-01", Reporter: "Chloe Wright" },
  { Ref: "FIR-019", Location: "Secunda", Status: "pending", Size: 280, Reported: "2026-05-31", Reporter: "Matthew Scott" },
  { Ref: "FIR-020", Location: "Hermanus", Status: "verified", Size: 90, Reported: "2026-05-30", Reporter: "Natalie Green" },
  { Ref: "FIR-021", Location: "Knysna", Status: "pending", Size: 150, Reported: "2026-05-29", Reporter: "Andrew Baker" },
  { Ref: "FIR-022", Location: "Soweto", Status: "verified", Size: 115, Reported: "2026-05-28", Reporter: "Victoria Adams" },
  { Ref: "FIR-023", Location: "Benoni", Status: "rejected", Size: 65, Reported: "2026-05-27", Reporter: "Jacob Nelson" },
  { Ref: "FIR-024", Location: "Boksburg", Status: "pending", Size: 170, Reported: "2026-05-26", Reporter: "Mia Carter" },
  { Ref: "FIR-025", Location: "Centurion", Status: "verified", Size: 125, Reported: "2026-05-25", Reporter: "Nathan Mitchell" },
  { Ref: "FIR-026", Location: "Krugersdorp", Status: "pending", Size: 230, Reported: "2026-05-24", Reporter: "Zoe Perez" },
  { Ref: "FIR-027", Location: "Vereeniging", Status: "verified", Size: 145, Reported: "2026-05-23", Reporter: "Luke Roberts" },
  { Ref: "FIR-028", Location: "Springs", Status: "rejected", Size: 50, Reported: "2026-05-22", Reporter: "Hannah Turner" },
  { Ref: "FIR-029", Location: "Alberton", Status: "pending", Size: 260, Reported: "2026-05-21", Reporter: "Gabriel Phillips" },
  { Ref: "FIR-030", Location: "Randburg", Status: "verified", Size: 135, Reported: "2026-05-20", Reporter: "Lily Campbell" },
];

export default function ReportTable() {
    const [statusFilter, setStatusFilter] = useState<'all' | ReportStatus>('all');

    

    return (
        <SideBarLayout>
            <div className="p-4 flex flex-col h-full w-full gap-y-3">
                            <header className="mb-6">
                                <h1 className="text-page-title font-display font-bold tracking-wider text-neutral uppercase">Reported Fires</h1>
                                <p className="font-body text-body text-neutral/50">View the reported fires</p>
                            </header>
                            {/* Header + filter + search */}
                            <div className="flex justify-between items-center">
                                    <StatusTableFilter filter={statusFilter} onChange={setStatusFilter}/>  
                                
                                    <TableSearchBar/>
                            </div>

                            {/* table */}
                            <ReportsTable requests={mockRequests} filter={statusFilter} onView={(req) => console.log(req)}/>       
                        </div>
        </SideBarLayout>
    )
}
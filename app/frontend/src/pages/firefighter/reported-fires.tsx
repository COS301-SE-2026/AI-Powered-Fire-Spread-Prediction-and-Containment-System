import React from 'react';
import { ReportRequest, ReportStatus } from "../../types/firefighter";
import { SideBarLayout } from '../../components/demoSidebar';
import { ReportsTable } from '../../components/firefighter/reportsTable';

const mockRequests: ReportRequest[] = [
  {
    Ref: "FIR-001",
    Location: "Johannesburg",
    Status: "pending",
    Size: 120,
    Reported: "2026-06-18",
    Reporter: "John Doe",
  },
];

export default function ReportTable() {
    return (
        <SideBarLayout>
            <div className="p-6 flex flex-col h-full w-full">
                            {/* Header + filter */}
                            <header className="mb-6">
                                <h1 className="text-3xl font-display font-bold tracking-wider text-neutral uppercase">Role Approvals</h1>
                                <p className="text-sm text-neutral/50 font-medium">Manage user role requests</p>
                            </header>
            
                            {/* table */}
                            <ReportsTable requests={mockRequests} filter='all' onView={(req) => console.log(req)}/>       
                        </div>
        </SideBarLayout>
    )
}
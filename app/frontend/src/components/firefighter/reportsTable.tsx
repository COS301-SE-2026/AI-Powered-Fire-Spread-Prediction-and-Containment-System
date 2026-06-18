import React from "react";
import { ReportRequest, ReportStatus } from "../../types/firefighter";

interface ReportsTableProp{
    requests: ReportRequest[];
    filter: 'all' | ReportStatus;
    onView: (request: ReportRequest) => void;
}

export function ReportsTable({ requests, filter, onView }: ReportsTableProp) {
    const filtered = requests.filter(req => 
        filter === 'all' || req.Status 
    );

    return (
        <div className="overflow-x auto">
            <table className="table">
                <thead>
                    <tr>
                        <th>Ref</th>
                        <th>Location</th>
                        <th>Status</th>
                        <th>Size</th>
                        <th>Reported</th>
                        <th>Reporter</th>
                    </tr>
                </thead>
                <tbody>
                    <tr className="hover:bg-[var(--color-surface-hover)]"> {/* row 1 */}
                        <th>ref example</th>
                        <th>location example</th>
                        <th>status example</th>
                        <th>size example</th>
                        <th>reported example</th>
                        <th>reporter example</th>
                    </tr>
                </tbody>
            </table>
        </div>
    )
}
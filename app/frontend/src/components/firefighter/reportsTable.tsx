import React from "react";
import { Report, ReportStatus } from "../../types/firefighter";

interface ReportsTableProp{
    requests: Report[];
    filter: 'all' | ReportStatus;
    onView: (request: Report) => void;
}

export function ReportsTable({ requests, filter, onView }: ReportsTableProp) {
    const filtered = requests.filter(req => 
        filter === 'all' || req.Status === filter
    );

    return (
        <div className="overflow-x-auto rounded-2xl border border-carbon-stroke max-h-[600px] w-full">
            <table className="table table-pin-rows">
                <thead>
                    <tr className="[&>th]:bg-carbon-bg [&>th]:border-b [&>th]:border-primary/40 ">
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase" >Ref</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase">Location</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase">Status</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase">Size</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase">Reported</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase">Reporter</th>
                    </tr>
                </thead>
                <tbody>
                    {filtered.length === 0 ? ( // no reports with any filyter which means table is empty
                        <tr>
                            <td colSpan={6} className="px-4 py-8 text-center text-sm font-bold text-error">
                                No reports in the table
                            </td>
                        </tr>
                    ) : (
                        filtered.map((req) => {
                            return(
                                <tr key={req.Ref} className="hover:bg-[var(--color-surface-hover)] even:bg-carbon-bg/80">
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.Ref}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.Location}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.Status}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.Size} ha</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.Reported}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.Reporter}</td>
                                </tr>
                            )
                        })
                    )}
                </tbody>
            </table>
        </div>
    )
}
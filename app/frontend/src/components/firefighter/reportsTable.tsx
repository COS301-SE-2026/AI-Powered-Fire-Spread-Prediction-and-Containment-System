import React from "react";
import { Report, ReportStatus } from "../../types/firefighter";
import { useRouter } from 'next/router';
import { StatusBadge } from "../admin/reportStatusBadge";

interface ReportsTableProp{
    readonly requests: Report[];
    readonly filter: 'all' | ReportStatus;
    readonly onView: (request: Report) => void;
}


export function ReportsTable({ requests, filter, onView }: ReportsTableProp) {
    const filtered = requests.filter(req => 
        filter === 'all' || req.status === filter
    );

    const router = useRouter();
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
                        <th className="text-left text-xs font-bold tracking-widest text-neutral uppercase"></th>
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
                                <tr key={req.ref} className="hover:bg-[var(--color-surface-hover)] even:bg-carbon-bg/80">
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.ref}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.location}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card"><StatusBadge status={req.status} /></td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.size} ha</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{new Date(req.reported).toLocaleDateString("en-ZA", {day: "2-digit", month: "2-digit", year: "numeric"})}</td>
                                    <td className="py-4 text-sm text-neutral border-t border-carbon-card">{req.reporter}</td>
                                    <td className="px-4 py-3">
                                        <button type="button" onClick={() => router.push(`/firefighter/${req.ref}`)} className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-carbon-card text-neutral/50 hover:bg-smoke-hover hover:text-neutral transition-colors">
                                            View
                                        </button>
                                    </td>
                                </tr>
                            )
                        })
                    )}
                </tbody>
            </table>
        </div>
    )
}
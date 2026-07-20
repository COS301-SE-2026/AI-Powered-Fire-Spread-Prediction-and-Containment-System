import React from "react";
import { FireReport, ReportStatus } from "../../types/report";
import { StatusBadge } from "./reportStatusBadge";
import { useRouter } from 'next/router';

interface FireReportsTableProps {
    readonly report: FireReport[];
    readonly filter: 'All' | ReportStatus;
}

export function FireReportsTable({ report, filter }: FireReportsTableProps) {
    const filtered = report.filter(r => filter === 'All' || r.status === filter)
        .sort((a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime());

    const router = useRouter();


    return (
        <div className="rounded-2xl border border-carbon-card overflow-hidden bg-carbon-side/60 shadow-xl shadow-black/30 max-h-[600px] overflow-y-auto">
            <table className="w-full">
                <thead className="sticky top-0 z-10">
                    <tr className="bg-carbon-bg border-b border-ignite/20">
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">Ref</th>
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">Location</th>
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">Status</th>
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">Size</th>
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">Reported</th>
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">Reporter</th>
                        <th className="text-left text-xs font-bold font-display tracking-widest text-neutral/40 uppercase px-4 py-3">View</th>
                    </tr>
                </thead>
                <tbody>
                    {filtered.length === 0 ? (
                        <tr>
                            <td colSpan={7} className="px-4 py-8 text-center text-sm text-neutral/30">
                                No requests found
                            </td>
                        </tr>
                    ) : (
                        filtered.map((report) => {
                            return (
                                <tr key={report.id} className="border-t border-carbon-card hover:bg-smoke-hover transition-colors even:bg-carbon-bg/30">
                                    <td className="px-4 py-3 font-mono text-xs text-flare">{report.reference_number}</td>
                                    <td className="px-4 py-3 text-sm text-neutral font-medium">{report.location_text}</td>
                                    <td className="px-4 py-3"><StatusBadge status={report.status} /></td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">{report.size} ha</td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">
                                        {new Date(report.submitted_at).toLocaleDateString('en-ZA', { day: 'numeric', month: 'short' })}
                                        {' | '}
                                        {new Date(report.submitted_at).toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' })}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">{report.reporter_name}</td>
                                    <td className="px-4 py-3">
                                        <button onClick={() => router.push(`/admin/${report.reference_number}`)} className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-carbon-card text-neutral/50 hover:bg-smoke-hover hover:text-neutral transition-colors">
                                            View
                                        </button>
                                    </td>
                                </tr>
                            );
                        })
                    )}
                </tbody>
            </table>
        </div>
    )
}
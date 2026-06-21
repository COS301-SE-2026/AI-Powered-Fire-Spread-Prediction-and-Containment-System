import React from "react";
import { FireReport, ReportStatus } from "../../types/report";
import { statusBadge, BadgeStyle } from "./statusBadge";
import { useRouter } from 'next/router';

interface FireReportsTableProps {
    report: FireReport[];
    filter: 'All' | ReportStatus;
}

export function FireReportsTable({ report, filter }: FireReportsTableProps) {
    const filtered = report.filter(r =>
        filter === 'All' || r.status === filter
    );

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
                            const badge: BadgeStyle = statusBadge[report.status] ?? statusBadge.none;
                            return (
                                <tr key={report.report_id} className="border-t border-carbon-card hover:bg-smoke-hover transition-colors even:bg-carbon-bg/30">
                                    <td className="px-4 py-3 font-mono text-xs text-flare">{report.report_id}</td>
                                    <td className="px-4 py-3 text-sm text-neutral font-medium">{report.location}</td>
                                    <td className="px-4 py-3">
                                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${badge.bg ? `${badge.bg} ${badge.text} ${badge.border}` : 'bg-carbon-card text-neutral/50'}`}>
                                            {report.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">{report.size}</td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">
                                        {report.reported_at.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short' })}
                                        {' · '}
                                        {report.reported_at.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' })}
                                    </td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">{report.reporter}</td>
                                    <td className="px-4 py-3">
                                        <button onClick={() => router.push(`/admin/${report.report_id}`)} className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-carbon-card text-neutral/50 hover:bg-smoke-hover hover:text-neutral transition-colors">
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
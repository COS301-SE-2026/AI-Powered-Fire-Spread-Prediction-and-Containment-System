import React from "react";
import { RoleRequest, RoleStatus } from "../../types/admin";
import { statusBadge, BadgeStyle } from "./statusBadge";

interface RoleRequestTableProps {
    requests: RoleRequest[];
    filter: 'All' | RoleStatus;
    onView: (request: RoleRequest) => void;
}

export function RoleRequestsTable({ requests, filter, onView }: RoleRequestTableProps) {
    const filtered = requests.filter(req =>
        filter === 'All' || req.status === filter
    );

    return (
        <div className="rounded-2xl border border-carbon-card overflow-hidden bg-carbon-side/60 shadow-xl shadow-black/30 max-h-[600px] overflow-y-auto">
            <table className="w-full">
                <thead className="sticky top-0 z-10">
                    <tr className="bg-carbon-bg border-b border-ignite/20">
                        <th className="text-left text-xs font-bold tracking-widest text-neutral/40 uppercase px-4 py-3">Name</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral/40 uppercase px-4 py-3">Email</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral/40 uppercase px-4 py-3">Role</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral/40 uppercase px-4 py-3">Date</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral/40 uppercase px-4 py-3">Status</th>
                        <th className="text-left text-xs font-bold tracking-widest text-neutral/40 uppercase px-4 py-3">View</th>
                    </tr>
                </thead>
                <tbody>
                    {filtered.length === 0 ? (
                        <tr>
                            <td colSpan={6} className="px-4 py-8 text-center text-sm text-neutral/30">
                                No requests found
                            </td>
                        </tr>
                    ) : (
                        filtered.map((req) => {
                            const badge: BadgeStyle = statusBadge[req.status] ?? statusBadge.none;
                            return (
                                <tr key={req.request_id} className="border-t border-carbon-card hover:bg-smoke-hover transition-colors even:bg-carbon-bg/30">
                                    <td className="px-4 py-3 text-sm text-neutral font-medium">{req.user_full_name}</td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">{req.email ?? '-'}</td>
                                    <td className="px-4 py-3 text-sm text-neutral/70 capatilize">{req.role}</td>
                                    <td className="px-4 py-3 text-sm text-neutral/70">
                                        {req.created_at ? new Date(req.created_at).toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' }) : '-'}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border capitalize ${badge.bg ? `${badge.bg} ${badge.text} ${badge.border}` : 'bg-carbon-card text-neutral/50'}`}>
                                            {req.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <button onClick={() => onView(req)} className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-carbon-card text-neutral/50 hover:bg-smoke-hover hover:text-neutral transition-colors">
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
import React from 'react';

export const DashboardMetrics:  React.FC = () => {
    return (
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

            <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider blocl mb-1">
                    Active Fires
                </span>
                <div className="text-3xl font-extrabold text-red-500">
                    12
                </div>
            </div>

            <div className="bg-slate-950 border border slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                    Pending Approvals
                </span>
                <div className="text-3xl font-extrabold text-amber-500">
                    5
                </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-500 ppercase tracking-wider block mb-1">
                    Total Users
                </span>
                <div className="text-3xl font-extrabold text-white">
                    284
                </div>
            </div>

            <div className="bg-slate-950 border border border-slate-800 p-5 rounded-xl">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                    System Status
                </span>
                <div className="text-3xl font-extrabold text-emarald-500 uppercase tracking-wide">
                    Okay
                </div>
            </div>
        </section>
    );
};
import React, { useState, useEffect } from 'react';

interface ActivityItem {
    message: string;
    timeAgo: string;
}

interface WeeklyData {
    day:string;
    count: number;
}

interface WeeklyData {
    day: string;
    count: number;
}

export const AdminDashBoardDetailed: React.FC = () => {
    const activityLog: ActivityItem[] = [
        {message: 'New fire reported - Pretoria West', timeAgo: '2 min ago'},
        {message: 'New fire reported - Pretoria West', timeAgo: '34 min ago'},
        {message: 'Fire contained - Centurion', timeAgo: '52 min ago'},
        {message: 'Role request submitted - T.Mokiena (Firefighter)', timeAgo: '1 hr ago'},
        {message: 'Role approved - A.Dlamini (Analyst)', timeAgo: '2 hr ago'},
        {message: 'AI spread simulation completed - Mamelodi', timeAgo: '2 hr ago'},
        {message: 'Containment line logged - Hatfield', timeAgo: '3 hr ago'},
    ];

    const weeklyIncidents: WeeklyData[] = [
        {day: 'Mon', count: 4},
        {day: 'Tue', count: 7},
        {day: 'Wed', count: 12},
        {day: 'Thu', count: 9},
        {day: 'Fri', count: 15},
        {day: 'Sat', count: 6},
        {day: 'Sun', count: 3},
    ];

    const maxCount = Math.max(...weeklyIncidents.map(d => d.count));

    const metrics: MiniMetric[] = [
        {
            title: 'Predictions completed',
            value: '142',
            subtext: 'Last 24 hours',
            icon: (
                <
            )
        }
    ]

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
            <div className="max-w-7xl mx-auto space-y-6">

                <div className="flex justify-between items-center mb-2">
                    <h1 className="text-xl font-bold tracking-tight text-white">
                        FireAway System Dashboard
                    </h1>
                    <span className="text-xs text-slate-400 font-mono">

                    </span>
                </div>

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

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    <section className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
                        <div>
                            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
                                Revent Activity
                            </h2>
                            <div className="divide-y divide-slate-800/60">
                                {activityLog.map((log, index) => (
                                    <div key={index} className="py-3 first:pt-0 last:pb-0 flex justify-between items-start space-x-4">
                                        <span className="text-sm font-medium text-slate-200 leading-snug">
                                            {log.message}
                                        </span>
                                        <span className="text-xs font-mono text-slate-500 whitespace-nowrap pt-0.5">
                                            {log.timeAgo}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    <section className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
                        <div>
                            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-6">
                                Incidents this week
                            </h2>

                            <div className="flex justify-between items-end h-56 pt-4 px-2 bg-slate-900/40 rounded-lg border border-slate-900/80">
                            {weeklyIncidents.map((data, index) => {
                                const percentageHeight = (data.count /maxCount) * 100;
                                return (
                                    <div key={index} className="flex flex-col items-center flex-1 group mx-1">
                                        <div className="text-[10px] font-mon text-slate-400 mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            {data.count}
                                         </div>   
                                         <div className="w-full bg-red-600/80 rounded-t-sm group-hover:bg-red-500 transition-colors"
                                         style={{height: `${percentageHeight}%`, minHeight: '4px'}}>
                                    </div>
                                    <span className="text-xs font-mono text-slate-500 mt-2 block">
                                        {data.day}
                                    </span>
                                    </div>
                                );
                            })}
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-slate-900 text-[11px] text-slate-500 font-mono flex justify-between">
                            <span>Y-Axis Max: {maxCount} Alerts</span>
                            <span> Spatial Log Distribution Context</span>
                        </div>
                    </section>
                </div>

            </div>
        </div>
    );
};

export default AdminDashBoardDetailed;
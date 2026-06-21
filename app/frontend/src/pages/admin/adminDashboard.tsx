//need to add sidebar still
import React, { useState, useEffect } from 'react';
import {DashboardMetrics} from '../../components/admin/adminDashboardMetrics';
import { MicrochipIcon, HeartWithPulseIcon, ChartLineIcon, DownloadIcon } from '../../components/admin/dashboardIcons';
import { SystemMetrics, MiniMetric } from '../../components/admin/systemMetrics';
import { LineChartIcon } from 'lucide-react';

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

    const bottomMetrics: MiniMetric[] = [
        {
            title: 'Predictions completed',
            value: '142',
            subtext: 'Last 24 hours',
            icon: <MicrochipIcon/>
        },
        {
            title: 'Model health',
            value: '142',
            subtext: 'Operational',
            icon: <HeartWithPulseIcon/>
        },
        {
            title: 'Avg. prediction confidence',
            value: '142',
            subtext: 'High confidence',
            statusText: 'High confidence',
            icon: <LineChartIcon/>
        },
        {
            title: 'Data source sync',
            value: '142',
            subtext: 'Updated 3 min ago',
            icon: <DownloadIcon/>
        },
    ];

    return (
        <div className="min-h-screen bg-base-100 text-base-content p-6 font-sans">
            <div className="max-w-7xl mx-auto space-y-6">

                <div className="border-b border-base-300 pb-3 mb-6">
                    <h1 className="text-4xl font-bold tracking-tight text-base-content font-display">
                        FireAway System Dashboard
                    </h1>
                </div>

                <DashboardMetrics/>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    <section className="bg-base-200 border border-base-300 rounded shadow-sm p-6 flex flex-col justify-between">
                        <div>
                            <h2 className="text-sm font-bold uppercase tracking-wider text-base-content/70 mb-4 font-display">
                                Recent Activity
                            </h2>
                            <div className="divide-y divide-base-300 border-b border-base-300">
                                {activityLog.map((log, index) => (
                                    <div key={index} className="py-3 px-2 flex justify-between items-start space-x-4 my-0.5 hover:bg-base-300 transition-colors">
                                        <span className="text-xs font-medium text-base-content leading-snug">
                                            {log.message}
                                        </span>
                                        <span className="text-[11px] font-mono text-base-content/60 whitespace-nowrap pt-0.5">
                                            {log.timeAgo}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    <section className="bg-base-200 border border-base-300 rounded shadow-sm p-6 flex flex-col justify-between min-h-[300px]">
                        <div>
                            <h2 className="text-sm font-bold uppercase tracking-wider text-base-content/70 mb-6 font-display">
                                Incidents this week
                            </h2>

                            <div className="flex justify-between items-end h-48 pt-4 px-4 bg-base-300/30 rounded border border-base-300">
                            {weeklyIncidents.map((data, index) => {
                                const percentageHeight = (data.count /maxCount) * 100;
                                return (
                                    <div key={index} className="flex flex-col items-center flex-1 group mx-1.5 h-full justify-end">
                                        <div className="text-[10px] font-mono text-primary mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            {data.count}
                                         </div>   
                                         <div className="w-full bg-primary/80 rounded-t-sm border-t border-x border-primary group-hover:bg-primary transition-colors"
                                         style={{height: `${percentageHeight}%`, minHeight: '4px'}}>
                                    </div>
                                    <span className="text-[10px] font-medium text-base-content/60 mt-2 block font-mono">
                                        {data.day}
                                    </span>
                                    </div>
                                );
                            })}
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-base-300 text-[11px] text-base-content/50 font-mono flex justify-between">
                            <span>Y-Axis Max: {maxCount} Alerts</span>
                            <span> Spatial Log Distribution Context</span>
                        </div>
                    </section>

                </div>

                <SystemMetrics metrics={bottomMetrics} />

            </div>
        </div>
    );
};

export default AdminDashBoardDetailed;
//need to add sidebar still
import React, {useState, useEffect} from 'react';
import {DashboardMetrics} from '../../components/admin/adminDashboardMetrics';
import { SystemMetrics, MiniMetric } from '../../components/admin/systemMetrics';
import { LineChartIcon, DownloadCloudIcon, MicrochipIcon, HeartIcon } from 'lucide-react';
import { AdminSideBarLayout } from '../../components/admin/adminSidebar';

interface ActivityItem {
    id: string;
    message: string;
    timeAgo: string;
}

interface WeeklyData {
    day: string;
    count: number;
}

interface TopMetricsData {
    active_fires: number;
    pending_approval: number;
    total_users: number;
    system_status: string;
}

interface SystemMetricsData {
    predictions_completed: number;
    model_health: string;
    avg_confidence_percent: number;
    last_sync_time: string;
}

interface DashboardResponse {
    top_metrics: TopMetricsData;
    activity_log: ActivityItem[];
    weekly_incidents: WeeklyData[];
    system_metrics: SystemMetricsData;
}

export const AdminDashBoardDetailed: React.FC = () => {
    const [data, setData] = useState<DashboardResponse | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            const token = localStorage.getItem('access_token');

            try {
                const response = await fetch('http://localhost:8000/api/admin/dashboard/summary', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorisation': `Bearer ${token}`
                    }
                });

                if (response.status === 401 || response.status === 403) {
                    setError('Access Denied. You do not have Admin privileges to view this dashboard');
                    setIsLoading(false);
                    return;
                }

                if (!response.ok) {
                    throw new Error('Failed to fetch dashboard data');
                }

                const result: DashboardResponse = await response.json();
                setData(result);
            } catch (err) {
                console.error("Dashboard fetch error:", err);
                setError('Unable to connect to the server. Ensure backend is running');
            } finally {
                setIsLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (isLoading) {
        return (
            <AdminSideBarLayout hideLoginRegister={true}>
                <div className="w-full min-h-screen flex items-center justify-center">
                    <span className="loading loading-spinner loading-lg text-primary"></span>
                </div>
            </AdminSideBarLayout>
        );
    }

    if (error || !data) {
        return (
            <AdminSideBarLayout hideLoginRegister={true}>
                <div className="alert alert-error bg-red-900/20 border border-red-900 text-red-400">
                    <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    <span>{error}</span>
                </div>
            </AdminSideBarLayout>
        )
    }

    const maxCount = Math.max(...data.weekly_incidents.map(d => d.count));

    const bottomMetrics: MiniMetric[] = [
        {
            title: 'Predictions completed',
            value: data.system_metrics.predictions_completed.toString(),
            subtext: 'Last 24 hours',
            icon: <MicrochipIcon className="w-5 h-5" />
        },
        {
            title: 'Model health',
            value: data.system_metrics.model_health,
            subtext: 'Operational',
            statusText: data.system_metrics.model_health === 'Operational' ? 'Operational' : 'Degraded',
            icon: <HeartIcon className="w-5 h-5" />
        },
        {
            title: 'Avg. prediction confidence',
            value: `${data.system_metrics.avg_confidence_percent}%`,
            subtext: 'High confidence',
            statusText: data.system_metrics.avg_confidence_percent > 80 ? 'High confidence' : 'Review needed',
            icon: <LineChartIcon className="w-5 h-5" />
        },
        {
            title: 'Data source sync',
            value: 'Connected',
            subtext: data.system_metrics.last_sync_time,
            icon: <DownloadCloudIcon className="w-5 h-5" />
        },
    ];

    return (
        <AdminSideBarLayout hideLoginRegister={true}>
            <div className="w-full space-y-6">

                <div className="border-b border-base-300 pb-3 mb-6">
                    <h1 className="text-4xl font-bold tracking-tight text-base-content font-display">
                        FireAway System Dashboard
                    </h1>
                </div>

                <DashboardMetrics metrics={data.top_metrics} />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">

                    <section className="bg-base-200 border border-base-300 rounded shadow-sm p-6 flex flex-col justify-between">
                        <div className="w-full">
                            <h2 className="text-sm font-bold uppercase tracking-wider text-base-content/70 mb-4 font-display">
                                Recent Activity
                            </h2>
                            <div className="divide-y divide-base-300 border-b border-base-300">
                                {data.activity_log.length === 0 ? (
                                    <div className="py-4 text-center text-sm text-base-content/50">No recemt activity</div> 
                                ) : (
                                    data.activity_log.map((log) => (
                                        <div key={log.id} className="py-3 px-2 flex justify-between items-start space-x-4 my-0.5 hover:bg-base-300 transition-colors">
                                            <span className="text-xs font-medium text-base-content leading-snug">
                                                {log.message}
                                            </span>
                                            <span className="text-[11px] font-mono text-base-content/60 whitespace-nowrap pt-0.5">
                                                {log.timeAgo}
                                            </span>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </section>

                    <section className="bg-base-200 border border-base-300 rounded shadow-sm p-6 flex flex-col justify-between min-h-[300px]">
                        <div className="w-full">
                            <h2 className="text-sm font-bold uppercase tracking-wider text-base-content/70 mb-6 font-display">
                                Incidents this week
                            </h2>

                            <div className="flex justify-between items-end h-48 pt-4 px-4 bg-base-300/30 rounded border border-base-300">
                            {data.weekly_incidents.map((data) => {
                                const percentageHeight = (data.count /maxCount) * 100;
                                return (
                                    <div key={data.day} className="flex flex-col items-center flex-1 group mx-1.5 h-full justify-end">
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
        </AdminSideBarLayout>
    );
};

export default AdminDashBoardDetailed;
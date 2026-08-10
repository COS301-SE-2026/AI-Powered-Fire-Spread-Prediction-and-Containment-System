export interface ActivityItem {
    id: string;
    message: string;
    timeAgo: string;
}


export interface WeeklyData{
    day: string;
    count: number;
}

export interface TopMetrics{
    active_fires: number;
    pending_approvals: number;
    total_users: number;
    system_status: string;
}

export interface SystemMetrics{
    predictions_completed: number;
    model_health: string;
    avg_confidence_percent: number;
    last_sync_time: string;
}

export interface DashboardSummaryResponse{
    top_metrics: TopMetrics;
    activity_log: ActivityItem[];
    weekly_incidents: WeeklyData[];
    system_metrics: SystemMetrics;
}

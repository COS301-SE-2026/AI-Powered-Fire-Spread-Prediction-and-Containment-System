export type ReportStatus = 'pending' | 'verified' | 'rejected';

export type FireReport = {
    report_id: string;
    location: string;
    status: ReportStatus;
    size: string;
    reported_at: Date;
    reporter: string;
    description?: string;
    lat?: number;
    lng?:number;
    image_url?: string;
}
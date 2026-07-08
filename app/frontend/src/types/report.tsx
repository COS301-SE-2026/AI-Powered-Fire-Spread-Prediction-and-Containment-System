export type ReportStatus = 'received' | 'pending' | 'verified' | 'rejected';

export type FireReport = {
    id: string;
    reference_number: string;
    location_text: string;
    status: ReportStatus;
    size: number;
    submitted_at: string;
    reporter_name: string;
    description?: string;
    image_url: string;
    lat: number;
    lng:number;
    status_index?: number;
}
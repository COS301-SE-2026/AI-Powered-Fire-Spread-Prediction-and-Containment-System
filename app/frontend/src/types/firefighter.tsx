export type ReportStatus = 'pending' | 'verified' | 'rejected';

export interface Report{
    ref: string;
    location: string; // have the api calculate the area using the data from POSTGIS
    status: ReportStatus;
    size: number;
    reported: string; // date and time that report was made
    reporter: string;
    description: string;
    img_url: string;
}

export interface ReportModal{
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

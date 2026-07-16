export type ReportStatus = 'pending' | 'verified' | 'received';

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
    ref: string;
    location: string;
    status: ReportStatus;
    reported: Date
    reporter: string;
    description: string;
    img_url: string;
    size: number;
}

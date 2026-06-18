export type ReportStatus = 'pending' | 'verified' | 'rejected';

export interface Report{ // come back and tweak to make sure it matches the API response when backend made
    Ref: string;
    Location: string; // have the api calculate the area using the data from POSTGIS
    Status: ReportStatus;
    Size: number;
    Reported: string; // date and time that report was made
    Reporter: string;
}

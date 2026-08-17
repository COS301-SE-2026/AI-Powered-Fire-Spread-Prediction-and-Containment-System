export type ReportStatus = 'received' | 'pending' | 'verified' | 'rejected';

export interface FireReportCreate {
  lat: number;
  lng: number;
  location_text: string;
  description: string | null;
  image_url: string | null;
  boundary_radius: number;
}

export interface FireReportMapResponse {
  id: string;
  reference_number: string;
  lat: number;
  lng: number;
  location_text: string;
  status: ReportStatus;
  boundary_radius: number;
  size: number;
  submitted_at: string;
  reporter_name: string | null;
}

export interface FireReportDetailResponse {
  id: string;
  reference_number: string;
  lat: number;
  lng: number;
  location_text: string;
  description: string | null;
  image_url: string;
  status: ReportStatus;
  boundary_radius: number;
  size: number;
  submitted_at: string;
  reporter_name: string | null;
}

import type { ReportStatus } from './Report';

export type FireStatus = 'active' | 'contained' | 'extinguised'

export interface FirefighterReportTable {
  id: string;
  ref: string;
  location: string;
  status: ReportStatus;
  size: number;
  reported: string;
  updated_at: string | null;
  reporter: string;
  verification_notes: string | null;
  lat: number;
  lng: number;
  fire_status: FireStatus;
  containment_percent: number | null;
  merged_into_id: string | null;
}

export interface FirefighterReportModal {
  id: string;
  ref: string;
  location: string;
  status: ReportStatus;
  reported: string;
  reporter: string;
  description: string;
  image_url: string;
  size: number;
  lat: number;
  lng: number;
}

export interface ReportList {
  data: FirefighterReportTable[];
  total: number;
}

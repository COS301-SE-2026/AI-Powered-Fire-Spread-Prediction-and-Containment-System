import type { ReportStatus } from './Report';

export interface FirefighterReportTable {
  id: string;
  ref: string;
  location: string;
  status: ReportStatus;
  size: number;
  reported: string;
  reporter: string;
  verification_notes: string | null;
  lat: number;
  lng: number;
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

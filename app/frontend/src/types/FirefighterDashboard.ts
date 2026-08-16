import type { ReportStatus } from './Report';

export type FireDanger = 'low' | 'medium' | 'high' | 'very high';

export interface NearbyFire {
  location_text: string;
  distance: number;
  time_ago: string;
  status: ReportStatus;
}

export interface EnvironmentVariables {
  wind: number;
  wind_dir: number;
  temperature: number;
  fire_danger: FireDanger;
  humidity: number;
}

export interface NearbyFiresList {
  data: NearbyFire[];
  total: number;
}

export interface DashboardData {
  nearby_fires: NearbyFiresList;
  environment_variables: EnvironmentVariables;
}

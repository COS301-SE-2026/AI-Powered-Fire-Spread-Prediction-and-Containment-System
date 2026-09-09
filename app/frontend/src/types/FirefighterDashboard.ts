import type { ReportStatus } from './Report';

export type FireDanger = 'low' | 'medium' | 'high' | 'very high';

export interface NearbyFire {
  id: string;
  reference_number: string;
  location_text: string;
  distance: number;
  time_ago: string;
  status: ReportStatus;
  lat: number;
  lng: number;
  boundary_radius: number;
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

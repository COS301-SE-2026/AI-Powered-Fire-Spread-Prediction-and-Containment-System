import type { RoleRequest } from './role-request';

export interface KPIs {
  total_users: number;
  pending_role_requests: number;
  total_firefighters: number;
  total_admins: number;
}

export interface AnalyticsData {
  kpis: KPIs;
  pending_requests: RoleRequest[];
}

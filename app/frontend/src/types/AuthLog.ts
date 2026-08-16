export type AuditAction =
  | 'Login'
  | 'Login Failed'
  | 'Logout'
  | 'Password Reset Requested'
  | 'Password Reset Completed'
  | 'Account Locked'
  | 'Account Unlocked'
  | 'Account Suspended'
  | 'Account Reactivated'
  | 'Role Request Submitted'
  | 'Role Request Approved'
  | 'Role Request Rejected'
  | 'Role Revoked'
  | 'Token Invalidated'
  | 'Simulation Run'
  | 'Simulation Re-run';

export interface AuditLogResponse {
  id: string;
  timestamp: string;
  user_email: string | null;
  action: AuditAction;
  detail: string | null;
}

export interface AuditLogListResponse {
  data: AuditLogResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

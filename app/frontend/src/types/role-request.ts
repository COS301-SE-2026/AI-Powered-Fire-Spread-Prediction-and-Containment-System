import type { UserRole } from './user';
export type RoleStatus = 'pending' | 'approved' | 'rejected' | 'revoked' | 'none';

export interface UserSummary{
    id: string;
    name: string;
    surname: string;
    email: string;
    license_number: string | null;
}

export interface RoleRequestCreate {
    current_role: UserRole;
}

export interface RoleRequest {
    request_id: string;
    user: UserSummary;
    requested_role: string;
    current_role: string;
    status: RoleStatus;
    firefighter_license_id: string | null;
    created_at: string;
    reviewed_by: string | null;
    reviewed_at: string | null;
}

export interface RoleRequestList {
    data: RoleRequest[];
    total: number;
}
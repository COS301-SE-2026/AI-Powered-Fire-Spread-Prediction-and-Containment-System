export type RoleStatus = 'pending' | 'approved' | 'rejected' | 'revoked' | 'none';

export interface UserSummary{
    id: string;
    name: string;
    surname: string;
    email: string;
    license_number?: string;
}

export interface RoleRequest {
    request_id: string;
    user: UserSummary;
    requested_role: string;
    current_role: string;
    status: RoleStatus;
    created_at?: string;
    reviewed_by?: string;
    reviewed_at?: string;
}
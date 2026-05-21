export type RoleStatus = 'pending' | 'approved' | 'rejected' | 'revoked' | 'none';

export interface RoleRequest {
    request_id: string;
    user_id: string;
    user_full_name: string;
    email?: string;
    role: string;
    status: RoleStatus;
    created_at?: string;
    firefighter_license_id?: string;
}
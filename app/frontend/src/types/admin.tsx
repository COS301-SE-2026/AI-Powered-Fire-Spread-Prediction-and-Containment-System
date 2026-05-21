export interface RoleRequest {
    request_id: string;
    user_id: string;
    user_full_name: string;
    role: 'user' | 'admin' | 'firefighter';
    status: 'pending' | 'approved' | 'rejected';
    firefigher_license_id?: string;
}
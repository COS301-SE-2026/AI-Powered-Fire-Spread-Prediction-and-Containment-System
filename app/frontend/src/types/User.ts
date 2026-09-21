export type UserRole = 'user' | 'firefighter' | 'admin';

export interface UserCreate {
  name: string;
  surname: string;
  email: string;
  id_number: string;
  role: UserRole;
}

export interface UserResponse {
  id: string;
  name: string;
  surname: string;
  email: string;
  role: UserRole;
  created_at: string;
  is_active: boolean;
}

import type { UserRole } from './User';

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  surname: string;
  id_number: string;
  license_number?: string | null;
  requested_role: UserRole | string | null;
}

export interface CompleteRegistrationRequest{
  registration_token: string;
  code: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResp {
  access_token: string;
  token_type: string;
}

export interface TwoFACreateResponse {
  otpauth_url: string;
}

export interface TwoFAVerifyRequest {
  username: string;
  code: string;
}

export interface MsgResponse {
  message: string;
}

export interface TwoFARequiredResponse {
  requires_2fa: boolean;
  email: string;
  otpauth_url: string | null;
  registration_token?: string;
  pending_approval: boolean;
}

export interface TwoFAVerifyResponse {
  role: UserRole | string;
  pending_approval: boolean;
}

export interface LoginResponse {
  role: UserRole;
  access_token: string;
}

import type { UserRole } from './User';

export interface RegisterRequest{
    email: string;
    password: string;
    name: string;
    surname: string;
    id_number: string;
    license_number?: string | null;

}

export interface LoginRequest {
    email: string;
    password: string;
}


export interface TokenResp{
    access_token: string;
    token_type: string;
}

export interface TwoFACreateResponse{
    otpauth_url: string;
}


export interface TwoFAVerifyRequest{
    username: string;
    code: string;
}


export interface MsgResponse{
    message: string;
}


export interface TwoFARequiredResponse{
    requires_2fa: boolean;
    email: string;
    otpauth_url: string | null;
}

export interface LoginResponse {
    role: UserRole;
}


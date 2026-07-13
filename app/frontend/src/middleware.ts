// Before protected pages load, checks cookie and user's role and redirects to login if user does not have access to page
import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import { jwtVerify } from 'jose';

const JWT_SECRET = process.env.JWT_SECURITY_KEY;

const protectedRoutes: {prefix: string; roles: string[]}[] = [
    {prefix: '/admin', roles: ['admin']},
    {prefix: '/firefighter', roles: ['firefighter']},
    {prefix: '/registeredUser', roles: ['user']},
];

export async function middleware(req: NextRequest) {
    const {pathname} = req.nextUrl;
    const matched = protectedRoutes.find(route => pathname.startsWith(route.prefix));

    if(!matched){
        return NextResponse.next();
    }

    const token = req.cookies.get('access_token')?.value;

    if (!token || !JWT_SECRET){
        return NextResponse.redirect(new URL('/login', req.url));
    }

    try {
        const secret = new TextEncoder().encode(JWT_SECRET);
        const {payload} = await jwtVerify(token, secret);
        const role = payload.role as string;

        if (!matched.roles.includes(role)){
            return NextResponse.redirect(new URL('/login', req.url));
        }
    } catch {
        return NextResponse.redirect(new URL('/login', req.url));   // if token missing/expired/signiture invalid
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/admin/:path*', '/firefighter/:path*', '/registeredUser/:path*'],
};

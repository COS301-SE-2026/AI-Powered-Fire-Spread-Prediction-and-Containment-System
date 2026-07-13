// Before protected pages load, checks cookie and user's role and redirects to login if user does not have access to page
import { NextResponse, NextRequest } from "next/server";
import { jwtVerify } from 'jose';

const JWT_SECRET = process.env.JWT_SECRET_KEY;

const protectedRoutes: {prefix: string; roles: string[]}[] = [
    {prefix: '/admin', roles: ['admin']},
    {prefix: '/firefighterDashboard', roles: ['firefighter']},
    {prefix: '/registeredUser', roles: ['user']},
];

function noStore(response: NextResponse): NextResponse{
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');
    return response;
}

export async function middleware(req: NextRequest) {
    const {pathname} = req.nextUrl;
    const matched = protectedRoutes.find(route => pathname.startsWith(route.prefix));

    if(!matched){
        return NextResponse.next();
    }

    const token = req.cookies.get('access_token')?.value;

    if (!token || !JWT_SECRET){
        return noStore(NextResponse.redirect(new URL('/login', req.url)));
    }

    try {
        const secret = new TextEncoder().encode(JWT_SECRET);
        const {payload} = await jwtVerify(token, secret);
        const role = payload.role as string;


        if (!matched.roles.includes(role)){
            return noStore(NextResponse.redirect(new URL('/login', req.url)));
        }
    } catch(err) {
        return noStore(NextResponse.redirect(new URL('/login', req.url)));   // if token missing/expired/signiture invalid
    }

    return noStore(NextResponse.next());
}

export const config = {
    matcher: ['/admin/:path*', '/firefighter/:path*', '/registeredUser/:path*'],
};


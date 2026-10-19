export function LiveMapRef(role: string, lat: number, lng: number): string {
    let base = '/users/live-map';
    if (role === 'admin') {
        base = '/admin/live-map';
    } else if (role === 'firefighter') {
        base = '/firefighter/dashboard';
    }
    return `${base}?lat=${lat}&lng=${lng}&zoom=12`;
}
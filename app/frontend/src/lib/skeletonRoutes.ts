export const SECTIONS = ['admin', 'firefighter', 'users', 'guests'];

export function isSectionRoute(url: string): boolean {
    const first = url.split('?')[0].split('#')[0].split('/')[1]?.toLowerCase() ?? '';
    return SECTIONS.includes(first);
}

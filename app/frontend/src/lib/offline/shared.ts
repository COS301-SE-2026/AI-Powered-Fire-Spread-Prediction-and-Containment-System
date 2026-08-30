// checks network reachability with health checks
export async function probeHealth(apiBaseUrl?: string): Promise<boolean> {
    if(typeof window === 'undefined') return false;
    if(!navigator.onLine) return false;

    const baseUrl = apiBaseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    try {
        const response = await fetch(`${baseUrl}/health`, {
            method: 'GET',
            cache: 'no-store',
            credentials: 'include',
            signal: controller.signal,
        });
        clearTimeout(timeoutId);
        return response.ok;
    } catch {
        clearTimeout(timeoutId);
        return false;
    }
}
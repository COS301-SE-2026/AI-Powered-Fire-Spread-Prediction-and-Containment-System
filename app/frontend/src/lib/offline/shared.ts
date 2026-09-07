// checks network reachability with health checks
let cachedHealthStatus: boolean | null = null
let lastProbeTime = 0;
let inflightProbe: Promise<boolean> | null = null

const CACHE_TTL_MS = 4000;

export function getStoredAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function resetHealthCache(): void {
  cachedHealthStatus = null;
  lastProbeTime = 0;
  inflightProbe = null;
}

export async function probeHealth(apiBaseUrl?: string): Promise<boolean> {
  if (typeof window === 'undefined') return false;
  if (!navigator.onLine) {
    cachedHealthStatus = false;
    lastProbeTime = Date.now();
    return false;
  }

  const now = Date.now();

  if (cachedHealthStatus !== null && now - lastProbeTime < CACHE_TTL_MS) {
    return cachedHealthStatus;
  }

  // duplicate callers share same fetch
  if (inflightProbe) {
    return inflightProbe;
  }

  const baseUrl = apiBaseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const healthBaseUrl = baseUrl.replace(/\/api\/?$/, '');
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 3000);

  try {
    const response = await fetch(`${healthBaseUrl}/health`, {
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

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export async function apiCall(endpoint: string, method: string = 'GET', body: unknown = null) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint: `/${endpoint}`;
  const url = `${API_URL}${cleanEndpoint}`

  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: body ? JSON.stringify(body) : undefined,
  });

  const contentType = res.headers.get('content-type');
  const hasJson = contentType && contentType.includes('application/json');
  const data = hasJson ? await res.json().catch(() => null) : null;

  if (!res.ok){
    const detail = (data && typeof data === 'object' && 'detail' in data ? String(data.detail) : null) ?? `Request failed(${res.status})`;
    throw new Error(detail);
  } 
  return data;
}

export async function logout() {
  try{
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if(!response.ok){
      console.error('Logout request failed with status:', response.status);
    }
  }catch (error) {
    console.error('Network error loading:', error);
  }finally{
    if(typeof window !== 'undefined'){
      localStorage.clear();
      sessionStorage.clear();
      window.location.assign('/login');
    }
  }
}

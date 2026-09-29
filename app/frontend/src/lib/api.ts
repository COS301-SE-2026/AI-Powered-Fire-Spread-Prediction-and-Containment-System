const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export async function apiCall(endpoint: string, method: string = 'GET', body: unknown = null) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint: `/${endpoint}`;

  let base = API_URL.replace(/\/+$/, '');
  if (base.endsWith('/api') && cleanEndpoint.startsWith('/api/')) {
    base = base.slice(0,-4);
  }

  const url = `${base}${cleanEndpoint}`

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
    let detail = `Request failed (${res.status})`;

    if(data && typeof data == 'object' && 'detail' in data){
      if(Array.isArray(data.detail) && data.detail[0]?.msg){
        detail = data.detail[0].msg.replace(/^Value error,\s*/, '');
      } else if(typeof data.detail === 'string'){
        detail = data.detail.replace(/^Value error,\s*/, '');
      } else {
        detail = JSON.stringify(data.detail);
      }
    }

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

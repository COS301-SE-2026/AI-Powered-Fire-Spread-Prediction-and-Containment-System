const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function apiCall(endpoint, method = "GET", body = null) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Something went wrong");
  return data;
}

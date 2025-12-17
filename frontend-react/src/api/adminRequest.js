// src/api/adminRequest.js
export async function adminRequest(path, { token, method = "GET", body, params } = {}) {
  if (!token) throw new Error("Нет токена (не авторизован)");

  const qs = params ? "?" + new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  ).toString() : "";

  const resp = await fetch(`/api/v1${path}${qs}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await resp.json().catch(() => ({}));

  if (!resp.ok) {
    const detail = data?.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map(e => e?.msg).filter(Boolean).join("; ")
          : (data?.message || `HTTP ${resp.status}`);
    throw new Error(msg);
  }

  return data;
}

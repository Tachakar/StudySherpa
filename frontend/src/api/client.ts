const API_BASE = "/api";
export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}
interface RequestOptions {
  path: string;
  method?: string;
  body?: object;
  token?: string;
}
async function request<T>(options: RequestOptions): Promise<T> {
  const { path, method = "GET", body, token } = options;
  const headers = new Headers({ "Content-Type": "application/json" });
  if (token !== undefined) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: method,
    body: JSON.stringify(body),
    headers: headers,
  });
  if (!response.ok) {
    const data = await response.json();
    const detail = data.detail ? data.detail : data.error;
    throw new ApiError(response.status, detail);
  } else if (response.status === 204) {
    return null as T;
  } else {
    const data = await response.json();
    return data as T;
  }
}

export default request;

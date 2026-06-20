export interface SessionView {
  user: string;
  token: string;
  message: string;
}

export async function login(email: string, password: string): Promise<SessionView> {
  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const payload = (await response.json()) as SessionView | { detail: string };
  if (!response.ok) {
    throw new Error("detail" in payload ? payload.detail : "Login failed.");
  }
  return payload as SessionView;
}

export interface HealthResponse {
  status: "ok";
  service: string;
  mode: "local";
}

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch("/api/health", {
    headers: {
      Accept: "application/json",
    },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}.`);
  }

  const payload: unknown = await response.json();

  if (
    typeof payload !== "object" ||
    payload === null ||
    !("status" in payload) ||
    payload.status !== "ok" ||
    !("service" in payload) ||
    typeof payload.service !== "string" ||
    !("mode" in payload) ||
    payload.mode !== "local"
  ) {
    throw new Error("Health response did not match the expected contract.");
  }

  return {
    status: payload.status,
    service: payload.service,
    mode: payload.mode,
  };
}

import { useCallback, useEffect, useState } from "react";

import { getHealth, type HealthResponse } from "../api/health";

type RuntimeState =
  | { phase: "loading" }
  | { phase: "connected"; health: HealthResponse }
  | { phase: "disconnected"; message: string };

export function RuntimeStatus() {
  const [runtime, setRuntime] = useState<RuntimeState>({ phase: "loading" });
  const [requestId, setRequestId] = useState(0);

  const checkAgain = useCallback(() => {
    setRuntime({ phase: "loading" });
    setRequestId((current) => current + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function checkHealth() {
      try {
        const health = await getHealth(controller.signal);
        setRuntime({ phase: "connected", health });
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }

        setRuntime({
          phase: "disconnected",
          message:
            error instanceof Error ? error.message : "Backend is unavailable.",
        });
      }
    }

    void checkHealth();

    return () => {
      controller.abort();
    };
  }, [requestId]);

  const isConnected = runtime.phase === "connected";
  const statusTitle =
    runtime.phase === "loading"
      ? "Checking backend"
      : isConnected
        ? "Backend connected"
        : "Backend unavailable";

  return (
    <section className="runtime-panel" aria-labelledby="runtime-heading">
      <h1 id="runtime-heading">Local runtime</h1>

      <div className="runtime-status" aria-live="polite">
        <span
          aria-hidden="true"
          className={`status-orb status-orb--${runtime.phase}`}
        />
        <div>
          <p className={`status-title status-title--${runtime.phase}`}>
            {statusTitle}
          </p>
          <p className="status-endpoint">GET /api/health</p>
          {runtime.phase === "disconnected" ? (
            <p className="status-detail">{runtime.message}</p>
          ) : null}
        </div>
      </div>

      <button
        className="check-button"
        disabled={runtime.phase === "loading"}
        onClick={checkAgain}
        type="button"
      >
        {runtime.phase === "loading" ? "Checking…" : "Check again"}
      </button>
    </section>
  );
}

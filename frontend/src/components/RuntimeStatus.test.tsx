import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RuntimeStatus } from "./RuntimeStatus";


afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("RuntimeStatus", () => {
  it("shows the connected state returned by the backend", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          status: "ok",
          service: "vibegraph-backend",
          mode: "local",
        }),
        { status: 200 },
      ),
    );

    render(<RuntimeStatus />);

    expect(
      await screen.findByText("Backend connected"),
    ).toBeInTheDocument();
  });

  it("can retry a failed health request", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response("unavailable", { status: 503 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            status: "ok",
            service: "vibegraph-backend",
            mode: "local",
          }),
          { status: 200 },
        ),
      );

    render(<RuntimeStatus />);
    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Check again" }));

    await waitFor(() => {
      expect(screen.getByText("Backend connected")).toBeInTheDocument();
    });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});

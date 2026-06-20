import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { INSTALL_COMMAND, InstallCommand } from "./InstallCommand";

describe("InstallCommand", () => {
  it("copies the scoped install command", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<InstallCommand />);
    fireEvent.click(screen.getByRole("button", { name: "Copy" }));

    expect(writeText).toHaveBeenCalledWith(INSTALL_COMMAND);
    expect(await screen.findByRole("button", { name: "Copied" })).toBeVisible();
  });
});

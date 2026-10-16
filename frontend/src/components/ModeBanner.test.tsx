import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({ getStatus: vi.fn() }));

// Replace the API layer, so no network is needed.
vi.mock("@/lib/api", () => ({ getStatus: mocks.getStatus }));

import { ModeBanner } from "./ModeBanner";

beforeEach(() => {
  mocks.getStatus.mockReset();
});

describe("ModeBanner", () => {
  it("explains demo mode when resumes are analyzed by keyword matching", async () => {
    mocks.getStatus.mockResolvedValue({ extraction_mode: "mock" });
    render(<ModeBanner />);

    const banner = await screen.findByRole("status");
    expect(banner).toHaveTextContent(/keyword matching/i);
    expect(banner).toHaveTextContent(/no external ai service/i);
  });

  it("shows nothing when an AI model is used", async () => {
    mocks.getStatus.mockResolvedValue({ extraction_mode: "ai" });
    render(<ModeBanner />);

    await waitFor(() => expect(mocks.getStatus).toHaveBeenCalledTimes(1));
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows nothing when the status cannot be loaded", async () => {
    mocks.getStatus.mockRejectedValue(new Error("offline"));
    render(<ModeBanner />);

    await waitFor(() => expect(mocks.getStatus).toHaveBeenCalledTimes(1));
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAccountSummary: vi.fn(),
  listResumes: vi.fn(),
  deleteResume: vi.fn(),
  deleteAllMyData: vi.fn(),
  deleteMyAccount: vi.fn(),
  signOut: vi.fn(),
  navigate: vi.fn(),
}));

// Replace the API layer, auth and navigation, so no network or login is needed.
vi.mock("@/lib/api", () => ({
  getAccountSummary: mocks.getAccountSummary,
  listResumes: mocks.listResumes,
  deleteResume: mocks.deleteResume,
  deleteAllMyData: mocks.deleteAllMyData,
  deleteMyAccount: mocks.deleteMyAccount,
  getErrorMessage: (_error: unknown, fallback: string) => fallback,
}));
vi.mock("@/lib/auth-context", () => ({
  useAuth: () => ({
    user: { id: "u1", email: "a@example.com" },
    session: null,
    isLoading: false,
    signOut: mocks.signOut,
  }),
}));
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => mocks.navigate };
});

import { SettingsPage } from "./SettingsPage";

beforeEach(() => {
  vi.restoreAllMocks();
  Object.values(mocks).forEach((mock) => mock.mockReset());

  mocks.getAccountSummary.mockResolvedValue({
    resumes: 2,
    analyses: 5,
    job_descriptions: 3,
  });
  mocks.listResumes.mockResolvedValue([
    { id: "r1", filename: "resume-a.pdf", created_at: "2026-10-01T10:00:00Z", skill_count: 11 },
    { id: "r2", filename: "resume-b.pdf", created_at: "2026-10-02T10:00:00Z", skill_count: 4 },
  ]);
  mocks.deleteResume.mockResolvedValue(undefined);
  mocks.deleteAllMyData.mockResolvedValue(undefined);
  mocks.deleteMyAccount.mockResolvedValue(undefined);
  mocks.signOut.mockResolvedValue(undefined);
});

describe("SettingsPage", () => {
  it("shows the data counts and the saved resumes", async () => {
    render(<SettingsPage />);

    expect(
      await screen.findByText(
        "You have 2 saved resumes, 5 analyses and 3 pasted job descriptions.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("resume-a.pdf")).toBeInTheDocument();
    expect(screen.getByText("resume-b.pdf")).toBeInTheDocument();
  });

  it("keeps account deletion disabled until DELETE is typed", async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await screen.findByText("resume-a.pdf");

    const button = screen.getByRole("button", { name: /delete my account/i });
    expect(button).toBeDisabled();

    await user.type(screen.getByLabelText(/type delete to confirm/i), "delete");
    expect(button).toBeDisabled();

    await user.clear(screen.getByLabelText(/type delete to confirm/i));
    await user.type(screen.getByLabelText(/type delete to confirm/i), "DELETE");
    expect(button).toBeEnabled();
  });

  it("deletes the account, signs out and returns home", async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);
    await screen.findByText("resume-a.pdf");

    await user.type(screen.getByLabelText(/type delete to confirm/i), "DELETE");
    await user.click(screen.getByRole("button", { name: /delete my account/i }));

    await waitFor(() => expect(mocks.signOut).toHaveBeenCalledTimes(1));
    expect(mocks.deleteMyAccount).toHaveBeenCalledTimes(1);
    expect(mocks.navigate).toHaveBeenCalledWith("/", { replace: true });
  });

  it("shows an error and stays signed in when account deletion fails", async () => {
    mocks.deleteMyAccount.mockRejectedValue(new Error("boom"));
    const user = userEvent.setup();
    render(<SettingsPage />);
    await screen.findByText("resume-a.pdf");

    await user.type(screen.getByLabelText(/type delete to confirm/i), "DELETE");
    await user.click(screen.getByRole("button", { name: /delete my account/i }));

    expect(
      await screen.findByText(/could not delete your account/i),
    ).toBeInTheDocument();
    expect(mocks.signOut).not.toHaveBeenCalled();
    expect(mocks.navigate).not.toHaveBeenCalled();
  });

  it("deletes a single resume after confirmation and reloads the list", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const user = userEvent.setup();
    render(<SettingsPage />);
    await screen.findByText("resume-a.pdf");

    await user.click(screen.getByRole("button", { name: /delete resume-a\.pdf/i }));

    await waitFor(() => expect(mocks.deleteResume).toHaveBeenCalledWith("r1"));
    await waitFor(() => expect(mocks.listResumes).toHaveBeenCalledTimes(2));
  });

  it("deletes all data after confirmation and keeps the user signed in", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const user = userEvent.setup();
    render(<SettingsPage />);
    await screen.findByText("resume-a.pdf");

    await user.click(screen.getByRole("button", { name: /delete all my data/i }));

    await waitFor(() => expect(mocks.deleteAllMyData).toHaveBeenCalledTimes(1));
    expect(
      await screen.findByText("All your saved data was deleted."),
    ).toBeInTheDocument();
    expect(mocks.signOut).not.toHaveBeenCalled();
  });
});
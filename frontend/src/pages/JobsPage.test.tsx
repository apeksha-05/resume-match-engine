import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ApiJob } from "@/lib/api-types";

const mocks = vi.hoisted(() => ({
  listJobs: vi.fn(),
  listResumes: vi.fn(),
  getRecommendations: vi.fn(),
  useAuth: vi.fn(),
}));

// Replace the API layer and auth, so no network, Supabase client or login is needed.
vi.mock("@/lib/api", () => ({
  listJobs: mocks.listJobs,
  listResumes: mocks.listResumes,
  getRecommendations: mocks.getRecommendations,
  getErrorMessage: (_error: unknown, fallback: string) => fallback,
}));
vi.mock("@/lib/auth-context", () => ({ useAuth: mocks.useAuth }));

import { JobsPage } from "./JobsPage";

function makeJob(overrides: Partial<ApiJob>): ApiJob {
  return {
    id: "job-1",
    title: "Backend Engineer",
    company: "Acme Cloud",
    description: "Build and test REST APIs.",
    location: "Bengaluru",
    work_mode: "hybrid",
    min_years: 3,
    required_skills: ["Python", "SQL"],
    preferred_skills: [],
    is_demo: true,
    created_at: "2026-10-01T00:00:00Z",
    ...overrides,
  };
}

function signedOut() {
  return { user: null, session: null, isLoading: false };
}

function renderJobsPage() {
  return render(
    <BrowserRouter>
      <JobsPage />
    </BrowserRouter>,
  );
}

beforeEach(() => {
  mocks.listJobs.mockReset();
  mocks.listResumes.mockReset();
  mocks.getRecommendations.mockReset();
  mocks.useAuth.mockReset();

  mocks.useAuth.mockReturnValue(signedOut());
  mocks.listResumes.mockResolvedValue([]);
  mocks.listJobs.mockResolvedValue({
    items: [
      makeJob({}),
      makeJob({ id: "job-2", title: "Junior Python Developer", min_years: 0 }),
    ],
    total: 2,
  });
});

describe("JobsPage", () => {
  it("shows the jobs returned by the API", async () => {
    renderJobsPage();

    expect(await screen.findByText("Backend Engineer")).toBeInTheDocument();
    expect(screen.getByText("Junior Python Developer")).toBeInTheDocument();
  });

  it("sends the search text to the API after the user stops typing", async () => {
    const user = userEvent.setup();
    renderJobsPage();
    await screen.findByText("Backend Engineer");

    await user.type(
      screen.getByPlaceholderText("Search title, company or location"),
      "python",
    );

    await waitFor(() =>
      expect(mocks.listJobs).toHaveBeenLastCalledWith(
        expect.objectContaining({ search: "python" }),
      ),
    );
  });

  it("shows an empty state when the API returns no jobs", async () => {
    mocks.listJobs.mockResolvedValue({ items: [], total: 0 });
    renderJobsPage();

    expect(
      await screen.findByText(/no jobs match these filters/i),
    ).toBeInTheDocument();
  });

  it("shows an error message when loading fails", async () => {
    mocks.listJobs.mockRejectedValue(new Error("boom"));
    renderJobsPage();

    expect(await screen.findByText(/could not load jobs/i)).toBeInTheDocument();
  });

  it("asks signed-out visitors to log in to rank jobs", async () => {
    renderJobsPage();

    expect(
      await screen.findByText(/log in to rank these jobs/i),
    ).toBeInTheDocument();
    expect(mocks.listResumes).not.toHaveBeenCalled();
  });

  it("tells signed-in users without saved resumes to run an analysis", async () => {
    mocks.useAuth.mockReturnValue({
      user: { id: "user-1", email: "a@example.com" },
      session: null,
      isLoading: false,
    });
    renderJobsPage();

    expect(
      await screen.findByText(/no saved resumes yet/i),
    ).toBeInTheDocument();
  });
});
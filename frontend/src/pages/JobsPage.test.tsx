import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { JobsPage } from "./JobsPage";

function renderJobsPage() {
  return render(
    <BrowserRouter>
      <JobsPage />
    </BrowserRouter>,
  );
}

describe("JobsPage", () => {
  it("shows all demo jobs by default", () => {
    renderJobsPage();
    expect(screen.getByText("Backend Engineer")).toBeInTheDocument();
    expect(screen.getByText("Junior Python Developer")).toBeInTheDocument();
    expect(screen.getByText("Data Engineering Intern")).toBeInTheDocument();
    expect(screen.getByText("Full Stack Developer")).toBeInTheDocument();
  });

  it("filters jobs by search text", async () => {
    const user = userEvent.setup();
    renderJobsPage();

    const searchBox = screen.getByPlaceholderText(
      "Search title, company or location",
    );
    await user.type(searchBox, "Backend");

    expect(screen.getByText("Backend Engineer")).toBeInTheDocument();
    expect(
      screen.queryByText("Junior Python Developer"),
    ).not.toBeInTheDocument();
  });

  it("shows an empty state when no jobs match", async () => {
    const user = userEvent.setup();
    renderJobsPage();

    const searchBox = screen.getByPlaceholderText(
      "Search title, company or location",
    );
    await user.type(searchBox, "nonexistent role xyz");

    expect(
      screen.getByText(/no jobs match these filters/i),
    ).toBeInTheDocument();
  });
});
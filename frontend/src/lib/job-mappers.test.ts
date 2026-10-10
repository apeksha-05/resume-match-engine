import { describe, expect, it } from "vitest";
import type { ApiJob, ApiRecommendation } from "./api-types";
import { toJobListItem, toRecommendationItem } from "./mappers";

const apiJob: ApiJob = {
  id: "job-1",
  title: "Backend Engineer",
  company: "Acme Cloud",
  description: "Build APIs.",
  location: "Bengaluru",
  work_mode: "hybrid",
  min_years: 3,
  required_skills: ["Python", "SQL"],
  preferred_skills: ["Redis"],
  is_demo: true,
  created_at: "2026-10-01T00:00:00Z",
};

describe("toJobListItem", () => {
  it("converts snake_case job fields and carries no score", () => {
    const item = toJobListItem(apiJob);

    expect(item.job.workMode).toBe("hybrid");
    expect(item.job.minYears).toBe(3);
    expect(item.job.requiredSkills).toEqual(["Python", "SQL"]);
    expect(item.job.preferredSkills).toEqual(["Redis"]);
    expect(item.job.isDemo).toBe(true);
    expect(item.score).toBeUndefined();
  });
});

describe("toRecommendationItem", () => {
  it("keeps the score and the matched and missing skills", () => {
    const recommendation: ApiRecommendation = {
      job: apiJob,
      score: 64,
      matched_skills: ["Python"],
      missing_skills: ["SQL", "Redis"],
    };

    const item = toRecommendationItem(recommendation);

    expect(item.job.title).toBe("Backend Engineer");
    expect(item.score).toBe(64);
    expect(item.matchedSkills).toEqual(["Python"]);
    expect(item.missingSkills).toEqual(["SQL", "Redis"]);
  });
});
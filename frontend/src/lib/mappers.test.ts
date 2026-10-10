import { describe, expect, it } from "vitest";
import type { ApiAnalysisDetail, ApiHistoryItem } from "./api-types";
import { toAnalysisResult, toHistoryItem } from "./mappers";

const apiAnalysis: ApiAnalysisDetail = {
  id: "a1",
  job_title: "Backend Engineer",
  company: "Acme Cloud",
  is_demo: true,
  created_at: "2026-10-01T10:00:00Z",
  overall_score: 52,
  weights: { skills: 0.45, semantic: 0.25, experience: 0.2, education: 0.1 },
  categories: [
    {
      key: "skills",
      label: "Skills coverage",
      score: 0.533,
      weight: 0.5,
      applicable: true,
      explanation: "e1",
    },
    {
      key: "education",
      label: "Education alignment",
      score: 0,
      weight: 0,
      applicable: false,
      explanation: "e2",
    },
  ],
  matched_required: [{ name: "Python", evidence: "Built APIs in Python" }],
  missing_required: ["Docker"],
  matched_preferred: [],
  missing_preferred: ["AWS"],
  evidence: [
    { requirement: "Python", snippet: "Built APIs in Python", similarity: 0.6 },
  ],
  calculation_notes: ["note"],
  suggestions: [
    { original: "o1", suggested: "s1", why_changed: "w1" },
    { original: "o2", suggested: "s2", why_changed: "w2" },
  ],
  roadmap: [
    { skill: "Docker", reason: "r", steps: ["step"], estimated_weeks: 2 },
  ],
};

describe("toAnalysisResult", () => {
  it("converts snake_case fields to camelCase", () => {
    const result = toAnalysisResult(apiAnalysis);

    expect(result.jobTitle).toBe("Backend Engineer");
    expect(result.isDemo).toBe(true);
    expect(result.createdAt).toBe("2026-10-01T10:00:00Z");
    expect(result.overallScore).toBe(52);
    expect(result.missingRequired).toEqual(["Docker"]);
    expect(result.matchedRequired[0].name).toBe("Python");
    expect(result.calculationNotes).toEqual(["note"]);
  });

  it("gives each suggestion a stable id and maps whyChanged", () => {
    const result = toAnalysisResult(apiAnalysis);

    expect(result.suggestions.map((s) => s.id)).toEqual(["s1", "s2"]);
    expect(result.suggestions[0].whyChanged).toBe("w1");
  });

  it("maps roadmap estimatedWeeks", () => {
    const result = toAnalysisResult(apiAnalysis);

    expect(result.roadmap[0].estimatedWeeks).toBe(2);
  });

  it("keeps the applicable flag on categories", () => {
    const result = toAnalysisResult(apiAnalysis);

    expect(result.categories[0].applicable).toBe(true);
    expect(result.categories[1].applicable).toBe(false);
  });
});

describe("toHistoryItem", () => {
  it("converts a history row", () => {
    const row: ApiHistoryItem = {
      id: "h1",
      job_title: "Data Analyst",
      company: "Coral Health",
      overall_score: 64,
      created_at: "2026-10-02T09:00:00Z",
    };

    expect(toHistoryItem(row)).toEqual({
      id: "h1",
      jobTitle: "Data Analyst",
      company: "Coral Health",
      overallScore: 64,
      createdAt: "2026-10-02T09:00:00Z",
    });
  });
});
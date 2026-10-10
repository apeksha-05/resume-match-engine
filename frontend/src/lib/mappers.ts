import type {
  ApiAnalysisDetail,
  ApiHistoryItem,
  ApiJob,
  ApiRecommendation,
} from "@/lib/api-types";
import type { AnalysisResult, HistoryItem, Job, JobListItem } from "@/types";

export function toAnalysisResult(api: ApiAnalysisDetail): AnalysisResult {
  return {
    id: api.id,
    jobTitle: api.job_title,
    company: api.company,
    isDemo: api.is_demo,
    createdAt: api.created_at,
    overallScore: api.overall_score,
    weights: api.weights,
    categories: api.categories.map((category) => ({
      key: category.key,
      label: category.label,
      score: category.score,
      weight: category.weight,
      applicable: category.applicable,
      explanation: category.explanation,
    })),
    matchedRequired: api.matched_required,
    missingRequired: api.missing_required,
    matchedPreferred: api.matched_preferred,
    missingPreferred: api.missing_preferred,
    evidence: api.evidence,
    suggestions: api.suggestions.map((suggestion, index) => ({
      id: `s${index + 1}`,
      original: suggestion.original,
      suggested: suggestion.suggested,
      whyChanged: suggestion.why_changed,
    })),
    roadmap: api.roadmap.map((item) => ({
      skill: item.skill,
      reason: item.reason,
      steps: item.steps,
      estimatedWeeks: item.estimated_weeks,
    })),
    calculationNotes: api.calculation_notes,
  };
}

export function toHistoryItem(api: ApiHistoryItem): HistoryItem {
  return {
    id: api.id,
    jobTitle: api.job_title,
    company: api.company,
    overallScore: api.overall_score,
    createdAt: api.created_at,
  };
}

export function toJob(api: ApiJob): Job {
  return {
    id: api.id,
    title: api.title,
    company: api.company,
    location: api.location,
    workMode: api.work_mode,
    minYears: api.min_years,
    description: api.description,
    requiredSkills: api.required_skills,
    preferredSkills: api.preferred_skills,
    isDemo: api.is_demo,
  };
}

export function toJobListItem(api: ApiJob): JobListItem {
  return { job: toJob(api) };
}

export function toRecommendationItem(api: ApiRecommendation): JobListItem {
  return {
    job: toJob(api.job),
    score: api.score,
    matchedSkills: api.matched_skills,
    missingSkills: api.missing_skills,
  };
}
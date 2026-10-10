import type { ApiAnalysisDetail, ApiHistoryItem } from "@/lib/api-types";
import type { AnalysisResult, HistoryItem } from "@/types";

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
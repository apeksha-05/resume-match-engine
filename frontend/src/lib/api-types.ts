import type { CategoryKey, WorkMode, Weights } from "@/types";

export interface ApiSkillMatch {
  name: string;
  evidence: string;
}

export interface ApiCategoryScore {
  key: CategoryKey;
  label: string;
  score: number;
  weight: number;
  applicable: boolean;
  explanation: string;
}

export interface ApiEvidenceItem {
  requirement: string;
  snippet: string;
  similarity: number;
}

export interface ApiBulletSuggestion {
  original: string;
  suggested: string;
  why_changed: string;
}

export interface ApiRoadmapItem {
  skill: string;
  reason: string;
  steps: string[];
  estimated_weeks: number;
}

export interface ApiAnalysisDetail {
  id: string;
  job_title: string;
  company: string;
  is_demo: boolean;
  created_at: string;
  overall_score: number;
  weights: Weights;
  categories: ApiCategoryScore[];
  matched_required: ApiSkillMatch[];
  missing_required: string[];
  matched_preferred: ApiSkillMatch[];
  missing_preferred: string[];
  evidence: ApiEvidenceItem[];
  calculation_notes: string[];
  suggestions: ApiBulletSuggestion[];
  roadmap: ApiRoadmapItem[];
}

export interface ApiHistoryItem {
  id: string;
  job_title: string;
  company: string;
  overall_score: number;
  created_at: string;
}

export interface ApiResume {
  id: string;
  filename: string;
  created_at: string;
}

export interface CreateAnalysisBody {
  resume_id: string;
  job_description_text: string;
  weights?: Weights;
}

export interface ApiJob {
  id: string;
  title: string;
  company: string;
  description: string;
  location: string;
  work_mode: WorkMode;
  min_years: number;
  required_skills: string[];
  preferred_skills: string[];
  is_demo: boolean;
  created_at: string;
}

export interface ApiJobList {
  items: ApiJob[];
  total: number;
}

export interface ApiResumeSummary {
  id: string;
  filename: string;
  created_at: string;
  skill_count: number;
}

export interface ApiRecommendation {
  job: ApiJob;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
}

export interface RecommendationsBody {
  resume_id: string;
  search?: string;
  work_mode?: WorkMode;
  max_years?: number;
  limit?: number;
}
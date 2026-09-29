export type WorkMode = "remote" | "hybrid" | "onsite";

/** Category weights. Values are between 0 and 1 and should sum to 1. */
export interface Weights {
  skills: number;
  semantic: number;
  experience: number;
  education: number;
}

export type CategoryKey = keyof Weights;

export interface CategoryScore {
  key: CategoryKey;
  label: string;
  /** Score between 0 and 1 */
  score: number;
  weight: number;
  /** Plain-English explanation of how this score was calculated */
  explanation: string;
}

export interface SkillMatch {
  name: string;
  /** Snippet copied from the resume that supports this skill */
  evidence: string;
}

export interface EvidenceItem {
  requirement: string;
  snippet: string;
  /** Cosine similarity between the requirement and the snippet */
  similarity: number;
}

export interface BulletSuggestion {
  id: string;
  original: string;
  suggested: string;
  whyChanged: string;
}

export interface RoadmapItem {
  skill: string;
  reason: string;
  steps: string[];
  estimatedWeeks: number;
}

export interface AnalysisResult {
  id: string;
  jobTitle: string;
  company: string;
  isDemo: boolean;
  createdAt: string;
  /** Overall score from 0 to 100. An estimated fit indicator, not a hiring probability. */
  overallScore: number;
  weights: Weights;
  categories: CategoryScore[];
  matchedRequired: SkillMatch[];
  missingRequired: string[];
  matchedPreferred: SkillMatch[];
  missingPreferred: string[];
  evidence: EvidenceItem[];
  suggestions: BulletSuggestion[];
  roadmap: RoadmapItem[];
  calculationNotes: string[];
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  workMode: WorkMode;
  minYears: number;
  description: string;
  requiredSkills: string[];
  preferredSkills: string[];
  isDemo: boolean;
}

export interface JobRecommendation {
  job: Job;
  /** Score from 0 to 100 */
  score: number;
  matchedSkills: string[];
  missingSkills: string[];
}

export interface HistoryItem {
  id: string;
  jobTitle: string;
  company: string;
  overallScore: number;
  createdAt: string;
}
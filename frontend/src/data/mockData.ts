import type {
  AnalysisResult,
  HistoryItem,
  Job,
  JobRecommendation,
  Weights,
} from "@/types";

export const defaultWeights: Weights = {
  skills: 0.45,
  semantic: 0.25,
  experience: 0.2,
  education: 0.1,
};

export const mockAnalysis: AnalysisResult = {
  id: "demo",
  jobTitle: "Backend Engineer",
  company: "Acme Cloud",
  isDemo: true,
  createdAt: "2026-09-20T10:30:00Z",
  overallScore: 71,
  weights: defaultWeights,
  categories: [
    {
      key: "skills",
      label: "Skills coverage",
      score: 0.667,
      weight: 0.45,
      explanation:
        "4 of 6 required skills matched (0.667) and 2 of 3 preferred skills matched (0.667). Formula: 0.8 x 0.667 + 0.2 x 0.667 = 0.667.",
    },
    {
      key: "semantic",
      label: "Semantic similarity",
      score: 0.76,
      weight: 0.25,
      explanation:
        "For each of 4 job requirements we took the closest resume passage, rescaled similarity with clamp((sim - 0.25) / 0.50, 0, 1), and averaged the results.",
    },
    {
      key: "experience",
      label: "Experience relevance",
      score: 0.6,
      weight: 0.2,
      explanation:
        "About 2 relevant years against 3 required gives 0.7 x 0.667 = 0.467. Title similarity of 0.44 adds 0.3 x 0.44 = 0.132. Total: 0.60.",
    },
    {
      key: "education",
      label: "Education and qualifications",
      score: 1,
      weight: 0.1,
      explanation:
        "A Bachelor's degree in Computer Science meets the job's Bachelor's degree requirement.",
    },
  ],
  matchedRequired: [
    {
      name: "Python",
      evidence: "Built REST endpoints in Python for a campus placement portal.",
    },
    {
      name: "FastAPI",
      evidence:
        "Developed a FastAPI service that handles resume uploads for a college project.",
    },
    {
      name: "SQL",
      evidence:
        "Designed PostgreSQL tables and wrote joins for reporting queries.",
    },
    {
      name: "REST APIs",
      evidence: "Documented and tested REST endpoints using Postman.",
    },
  ],
  missingRequired: ["Docker", "AWS"],
  matchedPreferred: [
    {
      name: "PostgreSQL",
      evidence:
        "Designed PostgreSQL tables and wrote joins for reporting queries.",
    },
    {
      name: "CI/CD",
      evidence:
        "Set up a GitHub Actions workflow that runs unit tests on every push.",
    },
  ],
  missingPreferred: ["Redis"],
  evidence: [
    {
      requirement: "Design and build REST APIs",
      snippet: "Built REST endpoints in Python for a campus placement portal.",
      similarity: 0.7,
    },
    {
      requirement: "Write unit and integration tests",
      snippet: "Wrote pytest tests for the scoring functions.",
      similarity: 0.62,
    },
    {
      requirement: "Work with relational databases",
      snippet:
        "Designed PostgreSQL tables and wrote joins for reporting queries.",
      similarity: 0.58,
    },
    {
      requirement: "Collaborate in an agile team",
      snippet:
        "Collaborated with a team of four using Git branches and pull requests.",
      similarity: 0.62,
    },
  ],
  suggestions: [
    {
      id: "s1",
      original: "Worked on backend of placement portal using Python.",
      suggested:
        "Built backend REST endpoints in Python and FastAPI for a campus placement portal.",
      whyChanged:
        "Names the framework and the kind of work, both already stated elsewhere in your resume. No new claims or numbers were added.",
    },
    {
      id: "s2",
      original: "Made database tables for the project.",
      suggested:
        "Designed PostgreSQL tables and wrote SQL joins for reporting queries.",
      whyChanged:
        "Uses the exact technology and task from your project description, which lines up with the job's SQL requirement.",
    },
    {
      id: "s3",
      original: "Used GitHub for testing.",
      suggested:
        "Configured a GitHub Actions workflow that runs unit tests on every push.",
      whyChanged:
        "Says precisely what you did. Only keep this wording if it is accurate for your project.",
    },
  ],
  roadmap: [
    {
      skill: "Docker",
      reason:
        "Required by this job and not shown anywhere in your resume, so it is a skill to learn, not one you have demonstrated.",
      steps: [
        "Install Docker Desktop and run your first container.",
        "Write a Dockerfile for one of your FastAPI projects.",
        "Use Docker Compose to run the app together with PostgreSQL.",
      ],
      estimatedWeeks: 2,
    },
    {
      skill: "AWS",
      reason:
        "Required by this job and not shown in your resume. Cloud basics are a common gap for students.",
      steps: [
        "Learn the core services: EC2, S3 and IAM.",
        "Deploy a small app using the free tier.",
        "Read the AWS Cloud Practitioner exam outline as a study guide.",
      ],
      estimatedWeeks: 4,
    },
  ],
  calculationNotes: [
    "Overall = 100 x (0.45 x 0.667 + 0.25 x 0.76 + 0.20 x 0.60 + 0.10 x 1.00) = 100 x 0.710 = 71.",
    "This is an estimated fit indicator. It is not a hiring probability and does not predict interview or hiring outcomes.",
    "All data on this page is fictional demo data.",
  ],
};

export const mockJobs: Job[] = [
  {
    id: "job-1",
    title: "Backend Engineer",
    company: "Acme Cloud",
    location: "Bengaluru",
    workMode: "hybrid",
    minYears: 3,
    description:
      "Design and build REST APIs, write tests, and work with relational databases in an agile team.",
    requiredSkills: ["Python", "FastAPI", "SQL", "REST APIs", "Docker", "AWS"],
    preferredSkills: ["PostgreSQL", "Redis", "CI/CD"],
    isDemo: true,
  },
  {
    id: "job-2",
    title: "Junior Python Developer",
    company: "Brightwave Labs",
    location: "Remote (India)",
    workMode: "remote",
    minYears: 0,
    description:
      "Build internal tools and automation scripts in Python with guidance from senior engineers.",
    requiredSkills: ["Python", "Git", "SQL"],
    preferredSkills: ["FastAPI", "Docker"],
    isDemo: true,
  },
  {
    id: "job-3",
    title: "Data Engineering Intern",
    company: "Northlake Analytics",
    location: "Pune",
    workMode: "hybrid",
    minYears: 0,
    description:
      "Help build data pipelines and clean datasets for the analytics team.",
    requiredSkills: ["Python", "SQL", "Pandas"],
    preferredSkills: ["Airflow", "PostgreSQL"],
    isDemo: true,
  },
  {
    id: "job-4",
    title: "Full Stack Developer",
    company: "Lumen Retail Tech",
    location: "Jaipur",
    workMode: "onsite",
    minYears: 2,
    description:
      "Build customer-facing web features using React on the front end and Python services on the back end.",
    requiredSkills: ["React", "TypeScript", "Python", "REST APIs"],
    preferredSkills: ["Tailwind CSS", "PostgreSQL"],
    isDemo: true,
  },
];

export const mockRecommendations: JobRecommendation[] = [
  {
    job: mockJobs[1],
    score: 82,
    matchedSkills: ["Python", "Git", "SQL", "FastAPI"],
    missingSkills: ["Docker"],
  },
  {
    job: mockJobs[0],
    score: 71,
    matchedSkills: ["Python", "FastAPI", "SQL", "REST APIs"],
    missingSkills: ["Docker", "AWS"],
  },
  {
    job: mockJobs[3],
    score: 64,
    matchedSkills: ["React", "TypeScript", "Python", "REST APIs"],
    missingSkills: [],
  },
  {
    job: mockJobs[2],
    score: 58,
    matchedSkills: ["Python", "SQL"],
    missingSkills: ["Pandas"],
  },
];

export const mockHistory: HistoryItem[] = [
  {
    id: "demo",
    jobTitle: "Backend Engineer",
    company: "Acme Cloud",
    overallScore: 71,
    createdAt: "2026-09-20T10:30:00Z",
  },
  {
    id: "h2",
    jobTitle: "Junior Python Developer",
    company: "Brightwave Labs",
    overallScore: 82,
    createdAt: "2026-09-18T14:05:00Z",
  },
  {
    id: "h3",
    jobTitle: "Data Engineering Intern",
    company: "Northlake Analytics",
    overallScore: 58,
    createdAt: "2026-09-15T09:45:00Z",
  },
];
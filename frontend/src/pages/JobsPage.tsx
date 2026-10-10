import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { SkillBadgeList } from "@/components/SkillBadgeList";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getErrorMessage,
  getRecommendations,
  listJobs,
  listResumes,
} from "@/lib/api";
import type { ApiResumeSummary } from "@/lib/api-types";
import { useAuth } from "@/lib/auth-context";
import { toJobListItem, toRecommendationItem } from "@/lib/mappers";
import type { JobListItem, WorkMode } from "@/types";

const workModeLabels: Record<WorkMode, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  onsite: "On-site",
};

const NO_RESUME = "none";
const SEARCH_DEBOUNCE_MS = 300;

interface LoadedJobs {
  key: string;
  items: JobListItem[];
  error: string | null;
}

interface LoadedResumes {
  userId: string;
  items: ApiResumeSummary[];
  error: string | null;
}

function JobCard({ item }: { item: JobListItem }) {
  const { job, score, matchedSkills, missingSkills } = item;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle>{job.title}</CardTitle>
            <CardDescription>
              {job.company} · {job.location} · {workModeLabels[job.workMode]}
            </CardDescription>
          </div>
          {score !== undefined && (
            <Badge className="shrink-0">{score}% fit</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">{job.description}</p>

        {score !== undefined && matchedSkills && missingSkills ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <SkillBadgeList
              title="Skills you match"
              skills={matchedSkills}
              variant="default"
              emptyText="None yet"
            />
            <SkillBadgeList
              title="Skills to build"
              skills={missingSkills}
              variant="outline"
              emptyText="None missing"
            />
          </div>
        ) : (
          <div className="flex flex-wrap gap-1.5">
            {job.requiredSkills.map((skill) => (
              <Badge key={skill} variant="secondary">
                {skill}
              </Badge>
            ))}
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          Experience:{" "}
          {job.minYears === 0 ? "entry level" : `${job.minYears}+ years`}
        </p>
        {job.isDemo && <Badge variant="outline">DEMO DATA</Badge>}
      </CardContent>
    </Card>
  );
}

export function JobsPage() {
  const { user } = useAuth();
  const userId = user?.id ?? null;

  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [workMode, setWorkMode] = useState<WorkMode | "all">("all");
  const [maxYears, setMaxYears] = useState<number | "all">("all");
  const [selectedResumeId, setSelectedResumeId] = useState(NO_RESUME);
  const [loadedResumes, setLoadedResumes] = useState<LoadedResumes | null>(null);
  const [loadedJobs, setLoadedJobs] = useState<LoadedJobs | null>(null);

  // Wait for the user to stop typing before calling the API.
  useEffect(() => {
    const timer = setTimeout(
      () => setDebouncedSearch(search.trim()),
      SEARCH_DEBOUNCE_MS,
    );
    return () => clearTimeout(timer);
  }, [search]);

  // Load the user's saved resumes, for the "rank for my resume" picker.
  useEffect(() => {
    if (!userId) return;

    let cancelled = false;
    listResumes()
      .then((items) => {
        if (!cancelled) setLoadedResumes({ userId, items, error: null });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLoadedResumes({
            userId,
            items: [],
            error: getErrorMessage(error, "Could not load your saved resumes."),
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  const resumes =
    userId !== null && loadedResumes !== null && loadedResumes.userId === userId
      ? loadedResumes
      : null;

  const activeResumeId =
    resumes !== null &&
    selectedResumeId !== NO_RESUME &&
    resumes.items.some((resume) => resume.id === selectedResumeId)
      ? selectedResumeId
      : null;

  const requestKey = JSON.stringify([
    debouncedSearch,
    workMode,
    maxYears,
    activeResumeId,
  ]);

  // Load jobs: ranked against a resume if one is selected, otherwise plain.
  useEffect(() => {
    let cancelled = false;

    const filters = {
      search: debouncedSearch || undefined,
      workMode: workMode === "all" ? undefined : workMode,
      maxYears: maxYears === "all" ? undefined : maxYears,
    };

    const request: Promise<JobListItem[]> = activeResumeId
      ? getRecommendations({
          resume_id: activeResumeId,
          search: filters.search,
          work_mode: filters.workMode,
          max_years: filters.maxYears,
          limit: 50,
        }).then((items) => items.map(toRecommendationItem))
      : listJobs(filters).then((result) => result.items.map(toJobListItem));

    request
      .then((items) => {
        if (!cancelled) setLoadedJobs({ key: requestKey, items, error: null });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLoadedJobs({
            key: requestKey,
            items: [],
            error: getErrorMessage(error, "Could not load jobs."),
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [activeResumeId, debouncedSearch, maxYears, requestKey, workMode]);

  const currentJobs =
    loadedJobs !== null && loadedJobs.key === requestKey ? loadedJobs : null;
  const isRanked = activeResumeId !== null;

  return (
    <div>
      <PageHeader
        title="Jobs"
        description="Sample job postings. All entries below are fictional demo data."
      />

      <div className="mb-6 grid gap-3 md:grid-cols-3">
        <Input
          placeholder="Search title, company or location"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          value={workMode}
          onValueChange={(value) => setWorkMode(value as WorkMode | "all")}
        >
          <SelectTrigger>
            <SelectValue placeholder="Work mode" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any work mode</SelectItem>
            <SelectItem value="remote">Remote</SelectItem>
            <SelectItem value="hybrid">Hybrid</SelectItem>
            <SelectItem value="onsite">On-site</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={String(maxYears)}
          onValueChange={(value) =>
            setMaxYears(value === "all" ? "all" : Number(value))
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Experience required" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any experience level</SelectItem>
            <SelectItem value="0">Entry level (0 years)</SelectItem>
            <SelectItem value="2">Up to 2 years</SelectItem>
            <SelectItem value="3">Up to 3 years</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">Rank jobs for my resume</CardTitle>
          <CardDescription>
            Uses the same explainable scoring as a full analysis. Scores are
            estimated fit indicators, not hiring probabilities.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!user && (
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-sm text-muted-foreground">
                Log in to rank these jobs against your resume.
              </p>
              <Button asChild size="sm">
                <Link to="/login">Log in</Link>
              </Button>
            </div>
          )}

          {user && resumes === null && (
            <Skeleton className="h-9 w-full max-w-md" />
          )}

          {user && resumes !== null && resumes.error !== null && (
            <p className="text-sm text-muted-foreground">{resumes.error}</p>
          )}

          {user &&
            resumes !== null &&
            resumes.error === null &&
            resumes.items.length === 0 && (
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-sm text-muted-foreground">
                  You have no saved resumes yet. Run an analysis first, then
                  come back to rank jobs.
                </p>
                <Button asChild size="sm">
                  <Link to="/analyze">New analysis</Link>
                </Button>
              </div>
            )}

          {user &&
            resumes !== null &&
            resumes.error === null &&
            resumes.items.length > 0 && (
              <div className="max-w-md">
                <Select
                  value={selectedResumeId}
                  onValueChange={setSelectedResumeId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a saved resume" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={NO_RESUME}>
                      Don't rank (show all jobs)
                    </SelectItem>
                    {resumes.items.map((resume) => (
                      <SelectItem key={resume.id} value={resume.id}>
                        {resume.filename} · {resume.skill_count} skills ·{" "}
                        {new Date(resume.created_at).toLocaleDateString()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
        </CardContent>
      </Card>

      {currentJobs === null && (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      )}

      {currentJobs !== null && currentJobs.error !== null && (
        <Alert variant="destructive">
          <AlertDescription>{currentJobs.error}</AlertDescription>
        </Alert>
      )}

      {currentJobs !== null &&
        currentJobs.error === null &&
        currentJobs.items.length === 0 && (
          <Card>
            <CardContent className="py-10 text-center text-sm text-muted-foreground">
              No jobs match these filters. Try widening your search.
            </CardContent>
          </Card>
        )}

      {currentJobs !== null &&
        currentJobs.error === null &&
        currentJobs.items.length > 0 && (
          <div>
            <p className="mb-3 text-sm text-muted-foreground">
              {currentJobs.items.length}{" "}
              {currentJobs.items.length === 1 ? "job" : "jobs"}
              {isRanked ? ", ranked by estimated fit for your resume." : "."}
            </p>
            <div className="grid gap-4 md:grid-cols-2">
              {currentJobs.items.map((item) => (
                <JobCard key={item.job.id} item={item} />
              ))}
            </div>
          </div>
        )}
    </div>
  );
}
import { useMemo, useState } from "react";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/ui/badge";
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
import { mockJobs, mockRecommendations } from "@/data/mockData";
import type { WorkMode } from "@/types";

const workModeLabels: Record<WorkMode, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  onsite: "On-site",
};

export function JobsPage() {
  const [search, setSearch] = useState("");
  const [workMode, setWorkMode] = useState<WorkMode | "all">("all");
  const [maxYears, setMaxYears] = useState<number | "all">("all");

  const filteredJobs = useMemo(() => {
    return mockJobs.filter((job) => {
      const matchesSearch =
        search.trim().length === 0 ||
        job.title.toLowerCase().includes(search.toLowerCase()) ||
        job.company.toLowerCase().includes(search.toLowerCase()) ||
        job.location.toLowerCase().includes(search.toLowerCase());
      const matchesMode = workMode === "all" || job.workMode === workMode;
      const matchesYears = maxYears === "all" || job.minYears <= maxYears;
      return matchesSearch && matchesMode && matchesYears;
    });
  }, [search, workMode, maxYears]);

  const scoreForJob = (jobId: string) =>
    mockRecommendations.find((rec) => rec.job.id === jobId)?.score;

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

      {filteredJobs.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            No jobs match these filters. Try widening your search.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredJobs.map((job) => {
            const score = scoreForJob(job.id);
            return (
              <Card key={job.id}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <CardTitle>{job.title}</CardTitle>
                      <CardDescription>
                        {job.company} · {job.location} ·{" "}
                        {workModeLabels[job.workMode]}
                      </CardDescription>
                    </div>
                    {score !== undefined && (
                      <Badge className="shrink-0">{score}% fit</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {job.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {job.requiredSkills.map((skill) => (
                      <Badge key={skill} variant="secondary">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                  {job.isDemo && (
                    <Badge variant="outline" className="mt-1">
                      DEMO DATA
                    </Badge>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
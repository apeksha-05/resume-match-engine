import { Download } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { CategoryScoreBar } from "@/components/CategoryScoreBar";
import { PageHeader } from "@/components/PageHeader";
import { ScoreDonut } from "@/components/ScoreDonut";
import { SkillBadgeList } from "@/components/SkillBadgeList";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { mockAnalysis } from "@/data/mockData";
import { downloadAnalysisReport, getAnalysis, getErrorMessage } from "@/lib/api";
import { saveBlob } from "@/lib/download";
import { useAuth } from "@/lib/auth-context";
import { toAnalysisResult } from "@/lib/mappers";
import type { AnalysisResult } from "@/types";

interface LoadedState {
  id: string;
  analysis: AnalysisResult | null;
  error: string | null;
}

function ResultsMessage({
  title,
  description,
  actionTo,
  actionLabel,
}: {
  title: string;
  description: string;
  actionTo: string;
  actionLabel: string;
}) {
  return (
    <div>
      <PageHeader title={title} description={description} />
      <Button asChild>
        <Link to={actionTo}>{actionLabel}</Link>
      </Button>
    </div>
  );
}

function ResultsLoading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-10 w-1/2" />
      <div className="grid gap-4 md:grid-cols-[auto_1fr]">
        <Skeleton className="h-64 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
      <Skeleton className="h-40 w-full" />
    </div>
  );
}

function AnalysisDashboard({ analysis }: { analysis: AnalysisResult }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  // The built-in demo is sample data that exists only in the browser,
  // so it has no server-side report to download.
  const canDownload = analysis.id !== mockAnalysis.id;

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);
    try {
      const blob = await downloadAnalysisReport(analysis.id);
      saveBlob(blob, `resume-match-report-${analysis.id}.pdf`);
    } catch (error) {
      setDownloadError(getErrorMessage(error, "Could not download the report."));
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-start justify-between gap-3">
        <PageHeader
          title={`${analysis.jobTitle} at ${analysis.company}`}
          description="Estimated fit indicator. This is not a hiring probability."
        />
        <Button
          variant="outline"
          disabled={!canDownload || isDownloading}
          title={canDownload ? undefined : "Log in and run an analysis to download a report"}
          onClick={handleDownload}
        >
          <Download className="mr-2 size-4" />
          {isDownloading ? "Preparing PDF..." : "Download report"}
        </Button>
      </div>

      {downloadError && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{downloadError}</AlertDescription>
        </Alert>
      )}

      {analysis.isDemo && (
        <Badge variant="outline" className="mb-4">
          DEMO DATA
        </Badge>
      )}

      <div className="grid gap-4 md:grid-cols-[auto_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Overall score</CardTitle>
          </CardHeader>
          <CardContent>
            <ScoreDonut score={analysis.overallScore} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Category breakdown</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {analysis.categories.map((category) => (
              <CategoryScoreBar key={category.key} category={category} />
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="text-base">Skills</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <SkillBadgeList
            title="Matched required skills"
            skills={analysis.matchedRequired.map((s) => s.name)}
            variant="default"
          />
          <SkillBadgeList
            title="Missing required skills"
            skills={analysis.missingRequired}
            variant="destructive"
            emptyText="None missing"
          />
          <SkillBadgeList
            title="Matched preferred skills"
            skills={analysis.matchedPreferred.map((s) => s.name)}
            variant="secondary"
          />
          <SkillBadgeList
            title="Missing preferred skills"
            skills={analysis.missingPreferred}
            variant="outline"
            emptyText="None missing"
          />
        </CardContent>
      </Card>

      <Card className="mt-4">
        <CardContent className="pt-6">
          <Tabs defaultValue="evidence">
            <TabsList>
              <TabsTrigger value="evidence">Evidence</TabsTrigger>
              <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
              <TabsTrigger value="roadmap">Learning roadmap</TabsTrigger>
              <TabsTrigger value="how">How this was scored</TabsTrigger>
            </TabsList>

            <TabsContent value="evidence" className="space-y-3 pt-4">
              {analysis.evidence.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Not enough text on the resume or job description to compare
                  passages.
                </p>
              ) : (
                analysis.evidence.map((item, index) => (
                  <div key={index} className="rounded-lg border p-3">
                    <p className="text-sm font-medium">{item.requirement}</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      "{item.snippet}"
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Similarity: {Math.round(item.similarity * 100)}%
                    </p>
                  </div>
                ))
              )}
            </TabsContent>

            <TabsContent value="suggestions" className="space-y-4 pt-4">
              {analysis.suggestions.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No suggestions yet. They are generated from the project and
                  work-experience bullet points found on your resume.
                </p>
              ) : (
                analysis.suggestions.map((s) => (
                  <div key={s.id} className="rounded-lg border p-3">
                    <div className="grid gap-3 md:grid-cols-2">
                      <div>
                        <p className="mb-1 text-xs font-medium uppercase text-muted-foreground">
                          Original
                        </p>
                        <p className="text-sm">{s.original}</p>
                      </div>
                      <div>
                        <p className="mb-1 text-xs font-medium uppercase text-muted-foreground">
                          Suggested
                        </p>
                        <p className="text-sm">{s.suggested}</p>
                      </div>
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      Why: {s.whyChanged}
                    </p>
                  </div>
                ))
              )}
              <p className="text-xs text-muted-foreground">
                Suggestions rephrase what you already wrote. Only keep wording
                that stays truthful to your real experience.
              </p>
            </TabsContent>

            <TabsContent value="roadmap" className="space-y-4 pt-4">
              {analysis.roadmap.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No missing required skills, so no learning roadmap is needed
                  for this job.
                </p>
              ) : (
                analysis.roadmap.map((item) => (
                  <div key={item.skill} className="rounded-lg border p-3">
                    <div className="mb-1 flex items-center justify-between">
                      <p className="font-medium">{item.skill}</p>
                      <Badge variant="outline">
                        ~{item.estimatedWeeks} weeks
                      </Badge>
                    </div>
                    <p className="mb-2 text-sm text-muted-foreground">
                      {item.reason}
                    </p>
                    <ul className="list-inside list-disc space-y-1 text-sm">
                      {item.steps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ul>
                  </div>
                ))
              )}
            </TabsContent>

            <TabsContent value="how" className="space-y-2 pt-4">
              <ul className="list-inside list-disc space-y-1 text-sm">
                {analysis.calculationNotes.map((note, i) => (
                  <li key={i}>{note}</li>
                ))}
              </ul>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}

export function ResultsPage() {
  const { id } = useParams();
  const { user, isLoading: authLoading } = useAuth();
  const [loaded, setLoaded] = useState<LoadedState | null>(null);

  const isDemo = id === mockAnalysis.id;
  const shouldFetch = Boolean(id) && !isDemo && Boolean(user);

  useEffect(() => {
    if (!shouldFetch || !id) return;

    let cancelled = false;
    getAnalysis(id)
      .then((result) => {
        if (!cancelled) {
          setLoaded({ id, analysis: toAnalysisResult(result), error: null });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLoaded({
            id,
            analysis: null,
            error: getErrorMessage(error, "Could not load this analysis."),
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [id, shouldFetch]);

  if (isDemo) {
    return <AnalysisDashboard analysis={mockAnalysis} />;
  }
  if (authLoading) {
    return <ResultsLoading />;
  }
  if (!user) {
    return (
      <ResultsMessage
        title="Log in to view this analysis"
        description="Saved analyses are private to your account."
        actionTo="/login"
        actionLabel="Log in"
      />
    );
  }

  const current = loaded && loaded.id === id ? loaded : null;
  if (current === null) {
    return <ResultsLoading />;
  }
  if (current.analysis === null) {
    return (
      <ResultsMessage
        title="Analysis not found"
        description={current.error ?? "This analysis could not be loaded."}
        actionTo="/history"
        actionLabel="Back to history"
      />
    );
  }
  return <AnalysisDashboard analysis={current.analysis} />;
}
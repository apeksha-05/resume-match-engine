import { Download, Link as LinkIcon } from "lucide-react";
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { mockAnalysis } from "@/data/mockData";

export function ResultsPage() {
  const { id } = useParams();

  if (id !== mockAnalysis.id) {
    return (
      <div>
        <PageHeader
          title="Analysis not found"
          description="Only the demo analysis exists until the backend is connected in Phase 4."
        />
        <Button asChild>
          <Link to="/results/demo">
            <LinkIcon className="mr-2 size-4" />
            Open the demo analysis
          </Link>
        </Button>
      </div>
    );
  }

  const analysis = mockAnalysis;

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-start justify-between gap-3">
        <PageHeader
          title={`${analysis.jobTitle} at ${analysis.company}`}
          description="Estimated fit indicator. This is not a hiring probability."
        />
        <Button variant="outline" disabled title="PDF export arrives in Phase 8">
          <Download className="mr-2 size-4" />
          Download report
        </Button>
      </div>

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
              {analysis.evidence.map((item, index) => (
                <div key={index} className="rounded-lg border p-3">
                  <p className="text-sm font-medium">{item.requirement}</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    "{item.snippet}"
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Similarity: {Math.round(item.similarity * 100)}%
                  </p>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="suggestions" className="space-y-4 pt-4">
              {analysis.suggestions.map((s) => (
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
              ))}
              <p className="text-xs text-muted-foreground">
                Suggestions rephrase what you already wrote. Only keep wording
                that stays truthful to your real experience.
              </p>
            </TabsContent>

            <TabsContent value="roadmap" className="space-y-4 pt-4">
              {analysis.roadmap.map((item) => (
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
              ))}
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
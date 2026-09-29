import { Link, useParams } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { mockAnalysis } from "@/data/mockData";

export function ResultsPage() {
  const { id } = useParams();

  if (id !== mockAnalysis.id) {
    return (
      <div>
        <PageHeader
          title="Analysis not found"
          description="Only the demo analysis exists until the backend is connected."
        />
        <Button asChild>
          <Link to="/results/demo">Open the demo analysis</Link>
        </Button>
      </div>
    );
  }

  const analysis = mockAnalysis;

  return (
    <div>
      <PageHeader
        title={`${analysis.jobTitle} at ${analysis.company}`}
        description="Estimated fit indicator, not a hiring probability."
      />
      {analysis.isDemo && <Badge variant="outline">DEMO DATA</Badge>}

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Overall score</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-5xl font-bold">
              {analysis.overallScore}
              <span className="text-xl text-muted-foreground"> / 100</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Category scores</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {analysis.categories.map((category) => (
              <div key={category.key}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>{category.label}</span>
                  <span>{Math.round(category.score * 100)}%</span>
                </div>
                <Progress value={category.score * 100} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <p className="mt-4 text-sm text-muted-foreground">
        Placeholder. Full results (skills, evidence, suggestions, roadmap) come
        in Phase 3C.
      </p>
    </div>
  );
}
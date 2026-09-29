import { PageHeader } from "@/components/PageHeader";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function NewAnalysisPage() {
  return (
    <div>
      <PageHeader
        title="New analysis"
        description="Upload a resume and provide a job description."
      />
      <Card>
        <CardHeader>
          <CardTitle>Coming in Phase 3C</CardTitle>
          <CardDescription>
            The upload form and job description input will be built here.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Placeholder page.
        </CardContent>
      </Card>
    </div>
  );
}
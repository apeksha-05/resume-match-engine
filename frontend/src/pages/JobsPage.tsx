import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { mockJobs } from "@/data/mockData";

export function JobsPage() {
  return (
    <div>
      <PageHeader
        title="Jobs"
        description="Sample job postings (fictional demo data). Filters and scores come in Phase 3C."
      />
      <div className="grid gap-4 md:grid-cols-2">
        {mockJobs.map((job) => (
          <Card key={job.id}>
            <CardHeader>
              <div className="flex items-center gap-2">
                <CardTitle>{job.title}</CardTitle>
                {job.isDemo && <Badge variant="outline">DEMO</Badge>}
              </div>
              <CardDescription>
                {job.company} · {job.location} · {job.workMode}
              </CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
}
import { Link } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent } from "@/components/ui/card";
import { mockHistory } from "@/data/mockData";

export function HistoryPage() {
  return (
    <div>
      <PageHeader
        title="Analysis history"
        description="Your saved analyses. Sample entries shown for now."
      />
      <div className="space-y-3">
        {mockHistory.map((item) => (
          <Card key={item.id}>
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <Link
                  to={`/results/${item.id}`}
                  className="font-medium hover:underline"
                >
                  {item.jobTitle}
                </Link>
                <p className="text-sm text-muted-foreground">
                  {item.company} ·{" "}
                  {new Date(item.createdAt).toLocaleDateString()}
                </p>
              </div>
              <span className="text-2xl font-semibold">
                {item.overallScore}
              </span>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
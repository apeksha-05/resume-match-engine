import { PageHeader } from "@/components/PageHeader";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function SettingsPage() {
  return (
    <div>
      <PageHeader
        title="Privacy and data"
        description="Controls for deleting your analyses and account."
      />
      <Card>
        <CardHeader>
          <CardTitle>Coming later</CardTitle>
          <CardDescription>
            Delete-analysis, delete-account and privacy notes will be added
            once authentication exists (Phase 8).
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Placeholder page.
        </CardContent>
      </Card>
    </div>
  );
}
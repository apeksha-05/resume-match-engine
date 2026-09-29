import { Link } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div>
      <PageHeader
        title="Page not found"
        description="That address does not exist."
      />
      <Button asChild>
        <Link to="/">Back to home</Link>
      </Button>
    </div>
  );
}
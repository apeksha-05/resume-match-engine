import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { deleteAnalysis, getErrorMessage, listAnalyses } from "@/lib/api";
import { toHistoryItem } from "@/lib/mappers";
import type { HistoryItem } from "@/types";

type HistoryState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; items: HistoryItem[] };

export function HistoryPage() {
  const [state, setState] = useState<HistoryState>({ status: "loading" });
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listAnalyses()
      .then((items) => {
        if (!cancelled) {
          setState({ status: "ready", items: items.map(toHistoryItem) });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setState({
            status: "error",
            message: getErrorMessage(error, "Could not load your history."),
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this analysis? This cannot be undone.")) return;

    setDeletingId(id);
    setActionError(null);
    try {
      await deleteAnalysis(id);
      setState((previous) =>
        previous.status === "ready"
          ? {
              status: "ready",
              items: previous.items.filter((item) => item.id !== id),
            }
          : previous,
      );
    } catch (error) {
      setActionError(getErrorMessage(error, "Could not delete this analysis."));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div>
      <PageHeader
        title="Analysis history"
        description="Your saved analyses. Only you can see them."
      />

      {actionError && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{actionError}</AlertDescription>
        </Alert>
      )}

      {state.status === "loading" && (
        <div className="space-y-3">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      )}

      {state.status === "error" && (
        <Alert variant="destructive">
          <AlertDescription>{state.message}</AlertDescription>
        </Alert>
      )}

      {state.status === "ready" && state.items.length === 0 && (
        <Card>
          <CardContent className="space-y-4 py-10 text-center">
            <p className="text-sm text-muted-foreground">
              You have no saved analyses yet.
            </p>
            <Button asChild>
              <Link to="/analyze">Run your first analysis</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {state.status === "ready" && state.items.length > 0 && (
        <div className="space-y-3">
          {state.items.map((item) => (
            <Card key={item.id}>
              <CardContent className="flex items-center justify-between gap-4 py-4">
                <div className="min-w-0">
                  <Link
                    to={`/results/${item.id}`}
                    className="block truncate font-medium hover:underline"
                  >
                    {item.jobTitle}
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    {item.company} ·{" "}
                    {new Date(item.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-semibold">
                    {item.overallScore}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete analysis"
                    disabled={deletingId === item.id}
                    onClick={() => handleDelete(item.id)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
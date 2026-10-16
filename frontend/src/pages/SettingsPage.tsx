import { AlertCircle, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  deleteAllMyData,
  deleteMyAccount,
  deleteResume,
  getAccountSummary,
  getErrorMessage,
  listResumes,
} from "@/lib/api";
import type { ApiAccountSummary, ApiResumeSummary } from "@/lib/api-types";
import { useAuth } from "@/lib/auth-context";

const CONFIRM_WORD = "DELETE";

interface LoadedData {
  key: number;
  summary: ApiAccountSummary | null;
  resumes: ApiResumeSummary[];
  error: string | null;
}

function countLabel(count: number, singular: string, plural: string): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

function PrivacyNotice() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>How your data is handled</CardTitle>
        <CardDescription>
          This is a portfolio project, not a commercial service. Here is what it does with your
          data.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="list-inside list-disc space-y-2 text-sm">
          <li>
            <span className="font-medium">What is saved:</span> your resume's file name, the skills
            and short text excerpts extracted from it, the details extracted from job descriptions
            you paste, and your analysis results (scores, suggestions and roadmap), all linked to
            your account.
          </li>
          <li>
            <span className="font-medium">What is not saved:</span> your PDF file is read in memory
            and is not stored, and the full text of your resume and job descriptions is not kept.
            The saved excerpts can still contain personal details that appear in them.
          </li>
          <li>
            <span className="font-medium">Who can see it:</span> only you. Everything is tied to
            your account, and the server checks this on every request. Sign-in is handled by
            Supabase Auth, so this app never sees or stores your password.
          </li>
          <li>
            <span className="font-medium">AI processing:</span> right now, skills are found with a
            built-in keyword matcher and semantic similarity is computed by a language model that
            runs on this app's own server, so your text is not sent to an external AI service. If
            external AI extraction is turned on in future, your resume text would be sent to that
            provider, and this notice will be updated before that happens.
          </li>
          <li>
            <span className="font-medium">Your control:</span> you can delete a single resume, all
            of your saved data, or your whole account below, at any time.
          </li>
        </ul>
      </CardContent>
    </Card>
  );
}

export function SettingsPage() {
  const { signOut } = useAuth();
  const navigate = useNavigate();

  const [refreshKey, setRefreshKey] = useState(0);
  const [loaded, setLoaded] = useState<LoadedData | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirmText, setConfirmText] = useState("");

  useEffect(() => {
    let cancelled = false;

    Promise.all([getAccountSummary(), listResumes()])
      .then(([summary, resumes]) => {
        if (!cancelled) {
          setLoaded({ key: refreshKey, summary, resumes, error: null });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLoaded({
            key: refreshKey,
            summary: null,
            resumes: [],
            error: getErrorMessage(error, "Could not load your saved data."),
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const current = loaded !== null && loaded.key === refreshKey ? loaded : null;

  const handleDeleteResume = async (resume: ApiResumeSummary) => {
    const confirmed = window.confirm(
      `Delete "${resume.filename}" and every analysis based on it? This cannot be undone.`,
    );
    if (!confirmed) return;

    setBusy(`resume:${resume.id}`);
    setActionError(null);
    setNotice(null);
    try {
      await deleteResume(resume.id);
      setNotice(`Deleted "${resume.filename}" and its analyses.`);
      setRefreshKey((key) => key + 1);
    } catch (error) {
      setActionError(getErrorMessage(error, "Could not delete this resume."));
    } finally {
      setBusy(null);
    }
  };

  const handleDeleteData = async () => {
    const confirmed = window.confirm(
      "Permanently delete all your saved resumes, analyses and job descriptions? Your login stays active. This cannot be undone.",
    );
    if (!confirmed) return;

    setBusy("data");
    setActionError(null);
    setNotice(null);
    try {
      await deleteAllMyData();
      setNotice("All your saved data was deleted.");
      setRefreshKey((key) => key + 1);
    } catch (error) {
      setActionError(getErrorMessage(error, "Could not delete your data."));
    } finally {
      setBusy(null);
    }
  };

  const handleDeleteAccount = async () => {
    setBusy("account");
    setActionError(null);
    setNotice(null);
    try {
      await deleteMyAccount();
    } catch (error) {
      setActionError(getErrorMessage(error, "Could not delete your account. Please try again."));
      setBusy(null);
      return;
    }
    await signOut();
    navigate("/", { replace: true });
  };

  const canDeleteAccount = confirmText === CONFIRM_WORD && busy === null;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <PageHeader
        title="Privacy and data"
        description="See what is stored about you, and delete it at any time."
      />

      {notice && (
        <Alert>
          <AlertDescription>{notice}</AlertDescription>
        </Alert>
      )}
      {actionError && (
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertDescription>{actionError}</AlertDescription>
        </Alert>
      )}

      <PrivacyNotice />

      <Card>
        <CardHeader>
          <CardTitle>Your saved data</CardTitle>
          {current !== null && current.summary !== null && (
            <CardDescription>
              {`You have ${countLabel(current.summary.resumes, "saved resume", "saved resumes")}, ${countLabel(current.summary.analyses, "analysis", "analyses")} and ${countLabel(current.summary.job_descriptions, "pasted job description", "pasted job descriptions")}.`}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {current === null && (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          )}

          {current !== null && current.error !== null && (
            <Alert variant="destructive">
              <AlertDescription>{current.error}</AlertDescription>
            </Alert>
          )}

          {current !== null && current.error === null && current.resumes.length === 0 && (
            <p className="text-sm text-muted-foreground">You have no saved resumes.</p>
          )}

          {current !== null && current.error === null && current.resumes.length > 0 && (
            <ul className="space-y-2">
              {current.resumes.map((resume) => (
                <li
                  key={resume.id}
                  className="flex items-center justify-between gap-3 rounded-lg border p-3"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{resume.filename}</p>
                    <p className="text-xs text-muted-foreground">
                      {resume.skill_count} skills ·{" "}
                      {new Date(resume.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Delete ${resume.filename}`}
                    disabled={busy !== null}
                    onClick={() => handleDeleteResume(resume)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </li>
              ))}
            </ul>
          )}

          <p className="mt-3 text-xs text-muted-foreground">
            Deleting a resume also deletes every analysis based on it.
          </p>
        </CardContent>
      </Card>

      <Card className="border-destructive/50">
        <CardHeader>
          <CardTitle>Delete your data</CardTitle>
          <CardDescription>These actions are permanent and cannot be undone.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="max-w-md text-sm text-muted-foreground">
              Delete all saved resumes, analyses and job descriptions. Your login stays active.
            </p>
            <Button variant="outline" disabled={busy !== null} onClick={handleDeleteData}>
              {busy === "data" ? "Deleting..." : "Delete all my data"}
            </Button>
          </div>

          <div className="space-y-3 border-t pt-6">
            <p className="text-sm text-muted-foreground">
              Delete your account: removes all your saved data and your login.
            </p>
            <div className="max-w-xs space-y-1.5">
              <Label htmlFor="confirm-delete">Type {CONFIRM_WORD} to confirm</Label>
              <Input
                id="confirm-delete"
                autoComplete="off"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
              />
            </div>
            <Button
              variant="destructive"
              disabled={!canDeleteAccount}
              onClick={handleDeleteAccount}
            >
              {busy === "account" ? "Deleting..." : "Delete my account"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

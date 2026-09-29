import { AlertCircle, FileText, Upload, X } from "lucide-react";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { WeightSliders } from "@/components/WeightSliders";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { defaultWeights } from "@/data/mockData";
import { formatFileSize, validateResumeFile } from "@/lib/validation";
import type { Weights } from "@/types";

export function NewAnalysisPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [weights, setWeights] = useState<Weights>(defaultWeights);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (candidate: File) => {
    const result = validateResumeFile(candidate);
    if (!result.valid) {
      setFileError(result.error ?? "Invalid file.");
      setFile(null);
      return;
    }
    setFileError(null);
    setFile(candidate);
  };

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) handleFile(dropped);
  };

  const canSubmit = file !== null && jobDescription.trim().length >= 50 && !isSubmitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setIsSubmitting(true);
    // No backend yet (that's Phase 4+). We simulate processing time,
    // then send the user to the existing demo analysis.
    await new Promise((resolve) => setTimeout(resolve, 1200));
    navigate("/results/demo");
  };

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title="New analysis"
        description="Upload a resume and paste a job description to see an explainable match score."
      />

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>1. Resume (PDF)</CardTitle>
            <CardDescription>Maximum size 5 MB, PDF only.</CardDescription>
          </CardHeader>
          <CardContent>
            {!file ? (
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={onDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed p-10 text-center transition-colors ${
                  isDragging
                    ? "border-primary bg-muted"
                    : "border-muted-foreground/30 hover:bg-muted/50"
                }`}
              >
                <Upload className="size-8 text-muted-foreground" />
                <p className="text-sm font-medium">
                  Drag and drop your resume, or click to browse
                </p>
                <p className="text-xs text-muted-foreground">PDF, up to 5 MB</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={(e) => {
                    const selected = e.target.files?.[0];
                    if (selected) handleFile(selected);
                  }}
                />
              </div>
            ) : (
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <FileText className="size-6 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setFile(null)}
                  aria-label="Remove file"
                >
                  <X className="size-4" />
                </Button>
              </div>
            )}
            {fileError && (
              <Alert variant="destructive" className="mt-3">
                <AlertCircle className="size-4" />
                <AlertTitle>Could not use this file</AlertTitle>
                <AlertDescription>{fileError}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>2. Job description</CardTitle>
            <CardDescription>
              Paste the full job posting text (at least 50 characters).
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Label htmlFor="jd" className="sr-only">
              Job description
            </Label>
            <Textarea
              id="jd"
              rows={8}
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
            <p className="mt-1 text-right text-xs text-muted-foreground">
              {jobDescription.trim().length} / 50 characters minimum
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>3. Category weights</CardTitle>
            <CardDescription>
              Optional. Adjust how much each category counts toward the
              overall score.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <WeightSliders weights={weights} onChange={setWeights} />
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button size="lg" disabled={!canSubmit} onClick={handleSubmit}>
            {isSubmitting ? "Analyzing..." : "Run analysis"}
          </Button>
        </div>
      </div>
    </div>
  );
}
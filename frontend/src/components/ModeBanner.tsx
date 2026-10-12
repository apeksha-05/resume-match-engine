import { Info } from "lucide-react";
import { useEffect, useState } from "react";
import { getStatus } from "@/lib/api";

type ExtractionMode = "mock" | "ai" | "unknown";

/**
 * A slim notice shown only when resumes are analyzed by the built-in keyword
 * matcher instead of an AI model, so the app never presents keyword matching
 * as AI.
 */
export function ModeBanner() {
  const [mode, setMode] = useState<ExtractionMode>("unknown");

  useEffect(() => {
    let cancelled = false;
    getStatus()
      .then((status) => {
        if (!cancelled) setMode(status.extraction_mode);
      })
      // If the status cannot be loaded, show nothing rather than guess.
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  if (mode !== "mock") return null;

  return (
    <div
      role="status"
      className="border-b bg-muted/60 px-4 py-2 text-center text-xs text-muted-foreground"
    >
      <Info className="mr-1.5 inline size-3.5 align-text-bottom" />
      Demo mode: skills are found by keyword matching against a built-in skill
      list, and suggestions follow fixed templates. No external AI service is
      used.
    </div>
  );
}
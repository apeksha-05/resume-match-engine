import type {
  ApiAnalysisDetail,
  ApiHistoryItem,
  ApiResume,
  CreateAnalysisBody,
} from "@/lib/api-types";
import { supabase } from "@/lib/supabase";

const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface ErrorBody {
  detail?: unknown;
}

/** Turns a FastAPI error response into a short, human-readable message. */
async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ErrorBody;
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((item: unknown) =>
          typeof item === "object" && item !== null && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : null,
        )
        .filter((message): message is string => message !== null);
      if (messages.length > 0) {
        return messages.join("; ");
      }
    }
  } catch {
    // The response had no JSON body, so fall through to the generic message.
  }
  return `Request failed with status ${response.status}.`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  const headers = new Headers(init.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(
      "Could not reach the server. Please check your connection and try again.",
      0,
    );
  }

  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

/** Returns the message of an ApiError, or the fallback for anything else. */
export function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback;
}

export function uploadResume(file: File): Promise<ApiResume> {
  const formData = new FormData();
  formData.append("file", file);
  // No Content-Type header here: the browser sets it, including the multipart boundary.
  return request<ApiResume>("/resumes", { method: "POST", body: formData });
}

export function deleteResume(id: string): Promise<void> {
  return request<void>(`/resumes/${encodeURIComponent(id)}`, { method: "DELETE" });
}

export function createAnalysis(body: CreateAnalysisBody): Promise<ApiAnalysisDetail> {
  return request<ApiAnalysisDetail>("/analyses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function getAnalysis(id: string): Promise<ApiAnalysisDetail> {
  return request<ApiAnalysisDetail>(`/analyses/${encodeURIComponent(id)}`);
}

export function listAnalyses(): Promise<ApiHistoryItem[]> {
  return request<ApiHistoryItem[]>("/analyses");
}

export function deleteAnalysis(id: string): Promise<void> {
  return request<void>(`/analyses/${encodeURIComponent(id)}`, { method: "DELETE" });
}
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Replace the real Supabase client, which needs environment variables.
vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: "test-token" } },
      }),
    },
  },
}));

import { ApiError, deleteAnalysis, getErrorMessage, listAnalyses } from "./api";

const fetchMock = vi.fn();

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("api request helper", () => {
  it("sends the Supabase access token as a bearer token", async () => {
    fetchMock.mockResolvedValue(jsonResponse([]));

    await listAnalyses();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url.endsWith("/analyses")).toBe(true);
    expect(new Headers(init.headers).get("Authorization")).toBe(
      "Bearer test-token",
    );
  });

  it("turns a FastAPI error string into an ApiError", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: "Analysis not found" }, 404));

    const error = await listAnalyses().catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(404);
    expect((error as ApiError).message).toBe("Analysis not found");
  });

  it("joins FastAPI validation messages", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(
        { detail: [{ msg: "String should have at least 50 characters" }] },
        422,
      ),
    );

    const error = await listAnalyses().catch((e: unknown) => e);

    expect((error as ApiError).message).toBe(
      "String should have at least 50 characters",
    );
  });

  it("reports an unreachable server with status 0", async () => {
    fetchMock.mockRejectedValue(new TypeError("fetch failed"));

    const error = await listAnalyses().catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(0);
    expect((error as ApiError).message).toMatch(/could not reach the server/i);
  });

  it("returns undefined for a 204 response", async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));

    await expect(deleteAnalysis("abc")).resolves.toBeUndefined();
  });
});

describe("getErrorMessage", () => {
  it("returns the message of an ApiError", () => {
    expect(getErrorMessage(new ApiError("Nope", 400), "fallback")).toBe("Nope");
  });

  it("returns the fallback for anything else", () => {
    expect(getErrorMessage(new Error("internal detail"), "fallback")).toBe(
      "fallback",
    );
  });
});
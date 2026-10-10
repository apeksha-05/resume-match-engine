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

import { ApiError, downloadAnalysisReport } from "./api";

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("downloadAnalysisReport", () => {
  it("requests the report with the bearer token and returns the file", async () => {
    const fakePdf = "%PDF-1.4 fake";
    fetchMock.mockResolvedValue(
      new Response(fakePdf, {
        status: 200,
        headers: { "Content-Type": "application/pdf" },
      }),
    );

    const blob = await downloadAnalysisReport("abc-123");

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url.endsWith("/analyses/abc-123/report.pdf")).toBe(true);
    expect(new Headers(init.headers).get("Authorization")).toBe(
      "Bearer test-token",
    );
    expect(blob.size).toBe(fakePdf.length);
    expect(blob.type).toBe("application/pdf");
  });

  it("throws an ApiError when the report is not found", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ detail: "Analysis not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const error = await downloadAnalysisReport("missing").catch(
      (e: unknown) => e,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(404);
    expect((error as ApiError).message).toBe("Analysis not found");
  });
});
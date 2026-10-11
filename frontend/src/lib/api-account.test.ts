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

import { deleteAllMyData, deleteMyAccount, getAccountSummary } from "./api";

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("account API calls", () => {
  it("reads the account summary with the bearer token", async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({ resumes: 1, analyses: 2, job_descriptions: 3 }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    const summary = await getAccountSummary();

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url.endsWith("/account/summary")).toBe(true);
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer test-token");
    expect(summary.analyses).toBe(2);
  });

  it("deletes all data with DELETE /account/data", async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));

    await expect(deleteAllMyData()).resolves.toBeUndefined();

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url.endsWith("/account/data")).toBe(true);
    expect(init.method).toBe("DELETE");
  });

  it("deletes the account with DELETE /account", async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));

    await expect(deleteMyAccount()).resolves.toBeUndefined();

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url.endsWith("/account")).toBe(true);
    expect(init.method).toBe("DELETE");
  });
});
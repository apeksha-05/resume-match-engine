import { describe, expect, it } from "vitest";
import { formatFileSize, validateResumeFile } from "./validation";

function makeFile(name: string, type: string, sizeBytes: number): File {
  const buffer = new Uint8Array(sizeBytes);
  return new File([buffer], name, { type });
}

describe("validateResumeFile", () => {
  it("accepts a valid small PDF", () => {
    const file = makeFile("resume.pdf", "application/pdf", 1024);
    expect(validateResumeFile(file)).toEqual({ valid: true });
  });

  it("rejects non-PDF files", () => {
    const file = makeFile("resume.docx", "application/msword", 1024);
    const result = validateResumeFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toMatch(/PDF/i);
  });

  it("rejects files larger than 5 MB", () => {
    const file = makeFile("resume.pdf", "application/pdf", 6 * 1024 * 1024);
    const result = validateResumeFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toMatch(/too large/i);
  });

  it("rejects empty files", () => {
    const file = makeFile("resume.pdf", "application/pdf", 0);
    const result = validateResumeFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toMatch(/empty/i);
  });
});

describe("formatFileSize", () => {
  it("formats bytes", () => {
    expect(formatFileSize(500)).toBe("500 B");
  });

  it("formats kilobytes", () => {
    expect(formatFileSize(2048)).toBe("2.0 KB");
  });

  it("formats megabytes", () => {
    expect(formatFileSize(3 * 1024 * 1024)).toBe("3.00 MB");
  });
});
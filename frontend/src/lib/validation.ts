const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB

export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

export function validateResumeFile(file: File): FileValidationResult {
  if (file.type !== "application/pdf") {
    return { valid: false, error: "Only PDF files are accepted." };
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: "File is too large. Maximum size is 5 MB.",
    };
  }
  if (file.size === 0) {
    return { valid: false, error: "This file appears to be empty." };
  }
  return { valid: true };
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
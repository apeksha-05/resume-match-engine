# Security and Privacy

This document describes what the project does to protect users and their data,
where each protection lives in the code, and what it does **not** protect
against. It describes the code as it is today. Anything that is not built is
listed under "Known limitations", not implied.

## 1. Data inventory

| Data | Stored? | Where | Notes |
|---|---|---|---|
| Resume PDF file | **No** | Memory only, discarded after parsing | Never written to disk or the database |
| Full resume text | **No** | Memory only | Not kept after extraction |
| Extracted skills + evidence snippets | Yes | `resumes.parsed` (Supabase Postgres) | Snippets are ~120-character excerpts; they can contain personal details |
| Resume file name | Yes | `resumes.filename` | Sanitized, max 120 characters |
| Pasted job description text | **No** | Memory only | Only the extracted title, skills and years are kept |
| Analysis results | Yes | `analyses` | Scores, evidence, suggestions, roadmap |
| Email and password | Yes | Supabase Auth | The app never sees or stores passwords |
| Request logs | Yes | Server logs | Method, path, status, client IP. Never resume text |

## 2. Controls

| Area | Control | Code | Verified by |
|---|---|---|---|
| Authentication | Supabase Auth; the backend verifies the ES256 token against the project's public keys. Only ES256, and `exp`, `sub` and `aud` are required. 10 seconds of clock skew allowed | `app/core/auth.py` | `tests/test_auth.py` |
| Authorization | Every row carries `user_id`. Other users' items return 404, so their existence is not revealed | `app/routers/*.py` | `tests/test_api_integration.py` |
| Deleted accounts | Endpoints that create data re-check that the account still exists | `require_existing_user` | `tests/test_auth.py` |
| Upload validation | PDF only, 5 MB streamed limit, PDF header check, 10-page limit, password-protected and unreadable files rejected, text capped at 100,000 characters | `app/services/pdf_extraction.py`, `uploads.py` | `tests/test_pdf_extraction.py`, `tests/test_uploads.py` |
| Input limits | Job description 50 to 20,000 characters, weights non-negative, search 100 characters | `app/schemas/*.py` | `tests/test_api_integration.py` |
| Rate limiting | 120 requests per minute per IP; hourly per-user limits on uploads, analyses, recommendations, reports and account changes | `app/core/rate_limit.py`, `limits.py` | `tests/test_rate_limit.py`, `tests/test_security_middleware.py` |
| Error handling | Unexpected errors return a generic 500. In production, logs record the error type and location, never its message | `app/core/security_middleware.py` | `tests/test_security_middleware.py`, `tests/test_api_integration.py` |
| Security headers | `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Cache-Control: no-store`, HSTS in production | `app/core/security_middleware.py` | `tests/test_security_middleware.py` |
| CORS | Only the configured frontend origin; only the methods and headers the app uses; no cookies | `app/main.py` | `tests/test_api_integration.py` |
| Secrets | Environment variables only; `.env` is git-ignored; the Supabase secret key is used only by the backend and never logged | `app/core/config.py`, `.gitignore` | History scans (`git log -S`) |
| Report output | User text is escaped and clipped before it enters the PDF | `app/services/report_pdf.py` | `tests/test_report_pdf.py` |
| User control | Delete one analysis, one resume, all data, or the whole account | `app/routers/account.py` | `tests/test_account_*.py` |

## 3. Prompt injection

Resumes and job descriptions are untrusted text. Defenses, in order of strength:

1. **Deterministic scoring.** The score is ordinary code. Resume text cannot change the formula or the weights.
2. **Strict output schema.** Anything an AI model returns must validate against a Pydantic schema.
3. **Evidence verification.** A skill is kept only if its evidence snippet really appears in the resume text.
4. **Safe prompt construction.** Text is wrapped in a random per-request boundary, and anything resembling the wrapper tags is removed (`app/services/prompt_safety.py`).
5. **Detection log.** Obvious instruction text is noted in the server log (the text itself is not logged).

Tests: `tests/test_prompt_safety.py`, `tests/test_injection_pipeline.py`, `tests/test_api_integration.py`.

## 4. Third-party processing

- **Supabase** stores accounts and saved data.
- **Hosting providers** run the frontend and backend once deployed.
- **AI providers:** in the current "demo mode", no resume text is sent to any external AI service. Skills are found by keyword matching, and semantic similarity is computed by a small language model that runs on the application's own server. If an external AI provider is enabled later, resume text would be sent to it for processing, and the in-app privacy notice and this document must be updated first.

## 5. Known limitations

- **Keyword stuffing.** A candidate can list skills they do not have. Evidence verification proves the text exists in the resume, not that the claim is true.
- **The external AI path has never run against a real service.** Its tests use a fake client, so they prove the surrounding plumbing, not the model's behavior.
- **Rate limits are in memory.** They reset on restart and are not shared between server instances.
- **Stale tokens.** A login token stays validly signed until it expires. Endpoints that create data re-check the account, but read endpoints do not (a deleted user has no data left to read).
- **Resume snippets can contain personal details,** and are stored until the user deletes them.
- **No malware scanning** of uploaded files. PDFs are parsed in memory, never executed, and limited in size and length.
- **Request logs include client IP addresses.**
- **Single region, no backups policy,** because this is a portfolio project, not a commercial service.

## 6. Before going live (deployment checklist)

- `ENVIRONMENT=production` (enables HSTS and message-free error logs)
- `SUPABASE_SECRET_KEY` set on the backend (uploads fail closed without it)
- `CORS_ORIGINS` set to the real frontend address
- `RATE_LIMIT_ENABLED=true`, and the proxy's forwarded addresses trusted so per-IP limits work
- A Content Security Policy configured on the frontend host
- Supabase email confirmation decision made
- Privacy notice re-read against the deployed behavior
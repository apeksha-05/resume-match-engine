# Matching Formula, API Contract, and Wireframes

## 1. Matching formula

The score is an **estimated fit indicator, not a hiring probability**.

```
overall = 100 * ( w_skills * S_skills
                + w_semantic * S_semantic
                + w_experience * S_experience
                + w_education * S_education )
```

Default weights (configurable, must sum to 1; normalized automatically):

| Category | Default weight |
|---|---|
| Skills coverage | 0.45 |
| Semantic similarity | 0.25 |
| Experience relevance | 0.20 |
| Education / qualifications | 0.10 |

### Category scores (each between 0 and 1)

**Skills coverage**
`S_skills = 0.8 * (matched_required / total_required) + 0.2 * (matched_preferred / total_preferred)`
If the JD has no preferred skills, `S_skills` equals the required ratio.

**Semantic similarity**
For each JD requirement or responsibility, take the maximum cosine similarity against all resume chunks. Convert to 0..1 with `clamp((sim - 0.25) / 0.50, 0, 1)`, then average. The 0.25 and 0.75 anchors are starting values and will be tuned in Phase 6 using sample data.

**Experience relevance**
`S_experience = 0.7 * min(1, relevant_years / required_years) + 0.3 * title_similarity`
If no years are required, the years part scores 1.

**Education / qualifications**
Compare degree level (diploma < bachelor < master < doctorate) and field relevance. Meets or exceeds gives 1; one level below gives 0.5; otherwise 0. If the JD states no education requirement, the category is not applicable.

### Not-applicable categories
If a category does not apply, its weight is redistributed proportionally across the others, and the UI says so.

### Explanation output
Every score returns its inputs: matched and missing skills, the best evidence snippet per requirement, each category's sub-calculation, and the weights used.

## 2. API contract (all under `/api/v1`)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Health check |
| GET | `/config/weights` | No | Default weights |
| POST | `/resumes` | Yes | Upload PDF, returns parsed resume |
| DELETE | `/resumes/{id}` | Yes | Delete resume and related data |
| POST | `/job-descriptions` | Yes | Parse pasted JD |
| GET | `/jobs` | Yes | List jobs (filters: role, location, min/max years, work_mode) |
| GET | `/jobs/{id}` | Yes | Job detail |
| POST | `/analyses` | Yes | Body: `resume_id`, JD text or `job_id`, optional weights |
| GET | `/analyses` | Yes | History list |
| GET | `/analyses/{id}` | Yes | Full result |
| GET | `/analyses/{id}/report.pdf` | Yes | Download PDF report |
| DELETE | `/analyses/{id}` | Yes | Delete analysis |
| POST | `/recommendations` | Yes | Body: `resume_id`, filters. Ranked jobs with scores |
| POST | `/demo/analysis` | No | Sample analysis for recruiters, no login |
| DELETE | `/account` | Yes | Delete all user data |

Standard error body: `{ "error": { "code": "string", "message": "string" } }`

## 3. Wireframe: results dashboard

```
+--------------------------------------------------------------+
| Logo    Dashboard | New Analysis | Jobs | History    [Avatar] |
+--------------------------------------------------------------+
| Backend Engineer at Acme (DEMO)                [Download PDF]|
| Estimated fit indicator - not a hiring probability           |
+-----------------+--------------------------------------------+
|  [ 72 / 100 ]   |  Skills        ######----  68%   w 0.45    |
|  donut chart    |  Semantic      #######---  74%   w 0.25    |
|                 |  Experience    ######----  60%   w 0.20    |
|                 |  Education     #########-  90%   w 0.10    |
+-----------------+--------------------------------------------+
| Matched skills  [Python][FastAPI][SQL]                       |
| Missing required [Docker][AWS]      Preferred [Redis]        |
+--------------------------------------------------------------+
| Tabs: Evidence | Suggestions | Learning roadmap | How scored |
+--------------------------------------------------------------+
| Original bullet        | Suggested revision   | Why changed  |
+--------------------------------------------------------------+
```

Pages: Landing, Login/Signup, New Analysis (upload + JD), Results, Jobs (filters + ranked cards), History, Settings/Privacy (delete data), Demo.
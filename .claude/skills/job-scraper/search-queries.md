# Search Queries for Job Scraper

Configured for Omar Martinosa - Seattle, WA. Four target directions: engineering
leadership, senior/staff frontend IC, AI/agentic tooling, and Forward Deployed Engineer.

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

## Search Sites

Primary:
- **linkedin.com/jobs** - covered by the `linkedin-search` CLI; the main source for US tech roles
- **WebSearch fallback** against ATS boards: `boards.greenhouse.io`, `jobs.lever.co`, `jobs.ashbyhq.com`, `job-boards.greenhouse.io`

Secondary (company career pages via WebSearch):
- AI labs: anthropic.com, openai.com, and peers
- Dev tools: vercel.com, sentry.io, linear.app, stripe.com, github.com
- Big tech, Seattle: amazon.jobs, microsoft.com/careers, google.com/about/careers, metacareers.com

Company lists are a **boost signal, not a filter**. Strong postings elsewhere still count.

## Query Categories

Location is wide open: fully remote (US), hybrid or onsite in the Seattle area, and
relocation are all acceptable. Run each query both with `Seattle` and with `remote`.

### Priority 1: AI / agentic tooling and Forward Deployed Engineer

The active growth direction, and the sharpest differentiator in the profile (20+ AI agents built).

```
site:boards.greenhouse.io "Forward Deployed Engineer"
site:jobs.ashbyhq.com "Forward Deployed Engineer"
site:jobs.lever.co "Forward Deployed Engineer" remote
site:linkedin.com/jobs "Forward Deployed Engineer" Seattle
site:linkedin.com/jobs "AI Engineer" TypeScript Seattle
site:boards.greenhouse.io "Applied AI Engineer"
site:linkedin.com/jobs "Developer Experience Engineer" AI remote
"agentic" "TypeScript" engineer jobs remote
```

### Priority 2: Senior / Staff frontend and product engineering

The bulk of the record: 20 years, React/Next.js, 100+ features to 70M+ customers.

```
site:linkedin.com/jobs "Staff Software Engineer" React Seattle
site:linkedin.com/jobs "Senior Software Engineer" React TypeScript Seattle
site:linkedin.com/jobs "Principal Frontend Engineer" remote
site:boards.greenhouse.io "Staff Frontend Engineer"
site:jobs.lever.co "Senior Frontend Engineer" React remote
site:jobs.ashbyhq.com "Product Engineer" TypeScript
```

### Priority 3: Engineering management and technical leadership

Current track. One year of formal EM scope, so target EM rather than Senior EM or Director.

```
site:linkedin.com/jobs "Engineering Manager" frontend Seattle
site:linkedin.com/jobs "Engineering Manager" "web" remote
site:boards.greenhouse.io "Engineering Manager" product engineering
site:jobs.lever.co "Engineering Manager" frontend
site:linkedin.com/jobs "Software Engineering Manager" Seattle
```

### Priority 4: Adjacent and wider net

Roles the profile supports but which are a pivot rather than a continuation.

```
site:linkedin.com/jobs "Technical Product Manager" frontend Seattle
site:linkedin.com/jobs "Solutions Engineer" developer tools remote
site:linkedin.com/jobs "Developer Advocate" TypeScript remote
site:linkedin.com/jobs "Technical Program Manager" engineering Seattle
site:boards.greenhouse.io "Solutions Architect" web
```

## Location Filter

No commute constraint. Treat all of these as in scope:
- Fully remote (US) - in scope
- Seattle / Bellevue / Redmond / Kirkland - in scope, no commute limit recorded
- Elsewhere in the US requiring relocation - in scope, note the city in the triage output
- Outside the US or requiring a visa - flag for the user rather than including silently

## Deal-breaker Filters

Drop or flag during triage:
- **Drop:** postings that ban or heavily restrict AI coding assistants
- **Drop:** postings where on-call rotation or production support is the primary responsibility
- **Flag:** posted compensation ranges that look low for the level. No numeric floor recorded, so surface it for the user rather than auto-rejecting. Missing range is not a flag.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape fde" -> Priority 1 queries plus custom FDE queries against specific AI labs
- "/scrape remote" -> every category, remote variants only

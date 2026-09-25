# skills.md — project skill & MCP registry

> Before installing a new skill or MCP, or searching a marketplace, check this
> file first. If the capability is listed, use it. If not, resolve it, install
> it, then ADD an entry here with a one-line "when to use".

## Active in this project

### Process
- **superpowers:brainstorming** — start of every sub-project (data, recsys, review models, audio, serving/UI).
- **superpowers:writing-plans / executing-plans** — spec → plan → build per sub-project.
- **superpowers:test-driven-development** — Claude-written code (`scripts/`, API). For Lucas's `src/groovn/`, suggest tests; he writes them.
- **superpowers:systematic-debugging** — unexpected metric values, leakage suspicions, training that doesn't converge.
- **superpowers:verification-before-completion** — run it, show output, then claim done.
- **grilling** — stress-test a modeling decision (split strategy, metric choice) before committing to it. Replaces `grill-me`.

### Review
- **code-review:code-review** — `/code-review` on a diff; use on Lucas's notebook-graduated code in `src/groovn/`.
- **pr-review-toolkit:review-pr** + specialist agents — before merging a sub-project.

### Stack
- **context7** (MCP) — current docs for `implicit`, PyTorch, DuckDB, pandas, MLflow, FastAPI. Use before answering API questions.
- **dataviz** — before any EDA / results chart (palette, form, accessibility).
- **NotebookEdit** (built-in) — scaffolding lesson notebooks.
- **ponytail** — minimal code in Claude-written parts. Never used to cut corners in teaching.

## Available but unused
- **webapp-testing** — Playwright checks once the web UI exists (sub-project 5).
- **codegraph** (MCP) — only once the codebase is big enough; `codegraph init` is Lucas's call.
- **Gamma / pptx / anthropic-skills:docs** — if a project write-up or deck is wanted.
- **artifact-design** — an HTML results page / model card, if wanted.

## Not installed yet (need a yes before installing)
- **frontend-design** — needed for sub-project 5 (web UI rebrand).
- **playwright** plugin — visual verification of the UI; `webapp-testing` may be enough.
- **github** plugin — `gh` CLI already covers PR/issue work, so likely skip.
- **fastapi-python** — sub-project 5.

## Known from past projects (seed catalog)

Seed data for `skills.md` → "Known from past projects". Source project: **ViralTrans**
(fleet management; FastAPI + PostgreSQL + Supabase + N8N; 2026).
Each entry: what it is · when it earned its place · how to invoke.

### Process / workflow

- **superpowers:brainstorming** — explore intent and requirements before any
  feature or behavior change. Invoke at the very start, before planning.
- **superpowers:writing-plans** — turn a spec into an ordered, checkpointed plan
  for a multi-step task.
- **superpowers:executing-plans** — execute a written plan with review
  checkpoints, in a fresh session.
- **superpowers:subagent-driven-development** — implement independent plan tasks
  via subagents in the current session.
- **superpowers:dispatching-parallel-agents** — 2+ independent tasks, no shared
  state; fan them out.
- **superpowers:test-driven-development** — every feature / bugfix: failing test
  first. Ran in strict mode on ViralTrans.
- **superpowers:systematic-debugging** — any bug or unexpected behavior:
  reproduce, hypothesize, prove. Used for the calendar monto-string bug and the
  orphaned `auth.users` bug.
- **superpowers:verification-before-completion** — before claiming done or
  committing: run the commands, show the output. Non-negotiable.
- **superpowers:requesting-code-review** — before merging a feature.
- **superpowers:receiving-code-review** — when acting on review feedback; verify
  before implementing.
- **superpowers:finishing-a-development-branch** — deciding how to integrate a
  completed branch.
- **superpowers:using-git-worktrees** — isolate feature work from the current
  workspace.
- **judgment-day** — explicit blind dual review with bounded fix rounds. Used for
  the autonomous PR-chain merges on the UI redesign.
- **grill-me** — stress-test a plan or design by relentless interview until every
  decision branch is resolved.

### Review

- **code-review:code-review** — `/code-review` on the current diff or a PR;
  correctness bugs + simplification. Levels low → ultra.
- **pr-review-toolkit:review-pr** — full multi-agent PR review.
- **pr-review-toolkit:silent-failure-hunter** — hunts swallowed errors and bad
  fallbacks. High value after error-handling changes.
- **pr-review-toolkit:type-design-analyzer** — reviews new types for
  encapsulation and invariants.
- **pr-review-toolkit:pr-test-analyzer** — test coverage / quality on a PR.
- **pr-review-toolkit:code-simplifier** — post-implementation clarity pass.
- **pr-review-toolkit:comment-analyzer** — comment accuracy / rot.

### Stack — Python / FastAPI / Postgres / Supabase

- **fastapi-python** — FastAPI best practices, async patterns. Core backend stack.
- **supabase:supabase** — any Supabase task: Auth, RLS, Edge Functions,
  migrations, client SSR, log queries, error triage.
- **supabase:supabase-postgres-best-practices** — load **before** writing or
  changing anything in Postgres: tables, column types, RLS policies + tests,
  indexes, triggers, functions, pg_cron / pgmq, pgvector, slow-query diagnosis.

### Frontend / design

- **frontend-design:frontend-design** — distinctive, non-templated UI direction.
  Used across the frontend redesign v1 / v2.
- **ui-ux-pro-max** — UI/UX database: styles, palettes, font pairings, UX
  guidelines, motion presets, chart types across many stacks.
- **ui-styling** — shadcn/ui + Tailwind + accessible components (dialogs,
  dropdowns, forms, tables), dark mode, theming.
- **design-system** — three-layer token architecture
  (primitive → semantic → component), component specs.

### Documents / decks

- **pptx** — any `.pptx` / `.potx`: create, read, edit. Built the 12-slide
  investor deck (PR #222).
- **slides** — strategic HTML presentations with Chart.js and design tokens.

### PR / repo hygiene

- **chained-pr** — split changes > 400 lines into stacked, individually
  reviewable PRs. The UI redesign chain (~30 PRs).
- **branch-pr** — create PRs with issue-first checks.
- **work-unit-commits** — plan commits as reviewable work units; tests + docs
  travel with the code.
- **issue-creation** — structured GitHub issues / bug reports.

### MCPs

- **supabase** — migrations, `get_advisors` (catches bad RLS + missing indexes),
  `query_logs`, `list_tables` before schema changes, `execute_sql`.
  Heaviest-used MCP on ViralTrans.
- **playwright** — screenshots for the investor deck; visual verification of the
  frontend redesign (not just green tests).
- **context7** — up-to-date library / framework docs; beats web search for API
  syntax and migration guides.
- **codegraph** — structural questions: call flow, callers / callees, blast
  radius, "how does X work". One call replaces a grep + read loop. Needs
  `codegraph init` per repo.
- **Gamma** — AI presentation / document generation; alternative path for decks.
- **github** — PR / issue / repo operations. (Configured on ViralTrans; auth
  failed one session — check the token.)
- **engram** — cross-session persistent memory (Gentleman-Programming). Optional
  if the native file memory suffices.

---

## Added this project
<none yet — date + reason + how to invoke>

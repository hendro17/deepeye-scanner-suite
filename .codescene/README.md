# CodeScene Configuration

## Overview

CodeScene Code Health analysis for **DeepEye Scanner Suite** — Python (FastAPI) + Vue 3 / TypeScript.

## Rule Sets

Defined in [`code-health-rules.json`](./code-health-rules.json):

| Rule Set | Language | Scope (`matching_content_path`) | Purpose |
|---|---|---|---|
| `backend-python` | Python | `api/**/*.py` | FastAPI bridge — routers, services, database |
| `frontend-vue-ts` | TypeScript / Vue | `web/**/*.{ts,vue,js}` | Vue 3 SPA — views, components, stores |

### Submodule Exclusion

The `scanner/deep-eye/` git submodule is **excluded** from all CodeScene analysis. It is upstream code (read-only, not our codebase). Exclusion is enforced by:

1. **Rule set scoping** — `matching_content_path` patterns target only `api/` and `web/`, never `scanner/`.
2. **`.gitignore`** — `scanner/deep-eye/reports/`, `scanner/deep-eye/logs/`, `scanner/deep-eye/data/` already ignored.
3. **CodeScene Cloud project settings** — when creating the project, add `scanner/deep-eye/**` to the exclude patterns.

## CI Integration

### GitHub Actions (`.github/workflows/code-health.yml`)

Runs `analyze_change_set` against `origin/main` on every PR and push to `main`.

**Setup:**
1. Create a CodeScene Personal Access Token (PAT) at [codescene.io](https://codescene.io) → Settings → Access Tokens.
2. Add it as a GitHub repository secret named `CS_ACCESS_TOKEN`.
3. The workflow installs `@codescene/codehealth-mcp` via npx and calls `analyze_change_set`.
4. Fails if any file degrades or quality gates don't pass.

### CodeScene Cloud GitHub App (Recommended — Supplementary)

For richer PR reviews (delta analysis, code health trends, knowledge maps):
1. Install the CodeScene GitHub App on the `hendro17/deepeye-scanner-suite` repo.
2. Connect the repo as a CodeScene project.
3. Set exclude pattern: `scanner/deep-eye/**`.
4. PRs get automatic code health status checks and inline comments.

## Local Usage

### Pre-Commit Safeguard

Before committing, run the CodeScene MCP pre-commit safeguard:

```bash
# Via MCP tools (cs-mcp must be running as your MCP server):
#   pre_commit_code_health_safeguard(git_repository_path=".")
#   analyze_change_set(base_ref="origin/main", git_repository_path=".")
```

### CLI Script

```bash
CS_ACCESS_TOKEN=pat_xxx python .codescene/scripts/code_health_check.py \
  --base-ref origin/main --repo .
```

## Thresholds

All thresholds use CodeScene defaults per language. Key values:

| Metric | Python | JS/TS |
|---|---|---|
| Function LoC warning | 70 | 70 |
| Function LoC alert | 500 | 500 |
| Cyclomatic complexity warning | 9 | 9 |
| Cyclomatic complexity alert | 100 | 100 |
| File LoC warning | 600 | 1000 |
| File LoC alert | 3000 | 5000 |
| Max function arguments | 4 | 4 |
| Nesting depth warning | 4 | 4 |

Override thresholds in `code-health-rules.json`. Validate after changes:

```bash
# Via MCP: rules_config_validate(config_path=".codescene/code-health-rules.json")
```

## Files

```
.codescene/
├── README.md                      # This file
├── code-health-rules.json         # Rule sets + thresholds (Python + Vue/TS)
└── scripts/
    └── code_health_check.py       # CI MCP client — calls analyze_change_set
```

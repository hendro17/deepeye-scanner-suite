# Spec: Phase 3.5 — Template Management (Pre-Docker)

## Goals
Make Templates tab editable — CRUD YAML templates without restart. Single source `scanner/deep-eye/templates/` on disk.

## Requirements
- **Storage**: shipped `templates/exposures/`, `templates/misconfig/` read-only. Custom writes → `templates/custom/` only.
- **Validation**: every create/update validates via `parse_template(text)` — must have `id`, `info.name`, `info.severity`, `http[]` with `path`/`raw`, severity in valid set. 400 + `TemplateError` message on fail.
- **ID uniqueness**: `id` must be unique across all dirs; duplicate → 409.
- **Backup**: on overwrite (PUT), save `.bak` timestamp.
- **Shipped protection**: DELETE/PUT on non-custom path → 403.
- **Reload**: `POST /api/templates/reload` re-scans `rglob("*.yaml")` without restart (stateless, no server reload needed — loader reads disk on scan start).
- **GET extend**: each entry: `id`, `name` (stem), `path` (relative), `tags`, `severity`, `http_count`, `enabled` (filter logic).
- **Web**: reuse Settings.vue Templates tab, no new route.
- **No submodule edit**: only writes to `templates/custom/` inside submodule workdir (git-ignored custom dir, not tracked).

## Non-Goals
- Monaco editor bundle (textarea sufficient — keeps deps minimal).
- Template execution engine changes (loader `load_templates` unchanged).

## API Contract
```
GET    /api/templates              → [{id, name, path, tags, severity, http_count, enabled}]
POST   /api/templates              body {id, content: yaml string} | file upload → 201 {id, path}
PUT    /api/templates/{id}         body {content} → 200
DELETE /api/templates/{id}         → 204 (403 if shipped)
POST   /api/templates/reload       → {count}
GET    /api/templates/{id}         → {id, content, path} (for edit/download)
```

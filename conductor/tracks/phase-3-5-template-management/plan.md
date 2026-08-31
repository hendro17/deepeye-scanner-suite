# Plan: Phase 3.5 — Template Management (Pre-Docker)

## Tasks
- [x] Task 1 — API CRUD: `POST /api/templates` (upload YAML), `PUT /api/templates/{id}` (edit), `DELETE /api/templates/{id}`, `POST /api/templates/reload`. Validate via `scanner/deep-eye/modules/template_engine/parser.py` (`parse_template`/`TemplateError`), reject bad YAML 400.
- [x] Task 2 — Extend `GET /api/templates`: return `id`, `info.name`, `info.severity`, `info.tags`, `http` summary, `enabled` derived from `templates.enabled` + tag/severity filters.
- [x] Task 3 — Web: Templates tab CRUD — table with Edit (textarea), Duplicate, Delete, Upload YAML, Download, Reload.
- [x] Task 4 — Config: `templates.enabled` toggle + `template_directories` + `tag_filters`/`severity_filter` editors in same tab via `PUT /api/config`.
- [x] Task 5 — Safety: writes only to `templates/custom/` (preserve `exposures/`/`misconfig/`), backup on overwrite, block overwrite of shipped without confirm — verified 403 for shipped.
- [x] Task 6 — Tests & gates: `api/tests/test_templates.py` updated + smoke CRUD verified, `web/src/views/Settings.providers.spec.ts` still green, `api/` 76 passed, `vitest` 39 passed, `vue-tsc` 0, `vite build` 59 modules.

## Dependencies
- Phase 3 done. Parser exists `scanner/deep-eye/modules/template_engine/parser.py:1`. Current `api/routers/templates.py:19` read-only.

## Execution Order
1 → 2 → 5 → 3 → 4 → 6 (5 safety before UI)

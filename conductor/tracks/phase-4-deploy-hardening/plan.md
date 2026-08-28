# Plan: Phase 4 — Deploy Hardening (Docker Compose, Auth, Persistence)

## Tasks
- [ ] Task 1 — Docker Compose spec & build: `docker-compose.yml` (api + web + optional chromium), `api/Dockerfile`, `web/Dockerfile`+`nginx.conf`, volumes & env_file. Verify `docker compose config` & `up --build`.
- [ ] Task 2 — Auth token middleware: `.env.example` (`DEEPEYE_AUTH_TOKEN`), FastAPI middleware `api/main.py:7` (CORSMiddleware + auth), `GET /api/health` exempt, tests.
- [ ] Task 3 — Persistence & health hardening: named volumes, `reports/`+`data/` mounts, healthcheck, README deploy notes (Caddy/Traefik), e2e smoke `docker compose up` → health + report persist.
- [ ] Task 4 — QA & gates: `pytest`/`vitest`/`playwright` green, `detect_changes --scope compare --base-ref main` (risk), `pnpm build` + `vue-tsc` pass, no HIGH/CRITICAL impact.

## Dependencies
- Phase 0-3 done (`plans/PLAN.md:371` ✅). No engine modification (`plans/SPEC.md:624`).

## Technical Notes
- Pin `plans/SPEC.md:574` compose structure, `sonar-project.properties:1` Quality Gate 80%.
- Keep `conductor/product.md` & `tech-stack.md` SSOT; update `README.md:196` install section after compose ready.
- GitNexus: `impact` sebelum edit `api/main.py:7` / `api/routers/*`, `detect_changes` sebelum commit.

## Execution Order
1 → 2 → 3 → 4 (sequential, each QA gate)

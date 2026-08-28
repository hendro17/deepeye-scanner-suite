# Spec: Phase 4 — Deploy Hardening (Docker Compose, Auth, Persistence)

## Goals
Menyelesaikan harden deploy agar `docker compose up` bisa serve full app (API + Web) secara reproducible, aman, dan persistent — closing gap Phase 4 di `plans/PLAN.md:295`.

## Requirements (from plans/SPEC.md:574 + plans/PLAN.md:295)
- `docker-compose.yml` dengan services:
  - `api`: `uvicorn api.main:app` (port 8000), mounts `scanner/`, `data/`, `reports/`, `scanner/deep-eye/config/config.yaml`, env_file `.env`
  - `web`: build Vue `dist/` serve via `nginx` atau `api` static (port 80/5173)
  - `chromium` optional profile `browser` (Playwright, `browserless/chrome`)
  - Volumes: named volumes untuk `api-data` + bind mounts `scanner/deep-eye/data`, `reports/`, `logs/`
- Auth: token-based local-first (`Authorization: Bearer <token>`), configurable via `.env` (`DEEPEYE_AUTH_TOKEN`), middleware FastAPI, open untuk local dev jika token kosong
- HTTPS: catatan reverse proxy Caddy/Traefik di README, tidak wajib di compose default
- Persistence: reports + SQLite (`data/suite.db` / `scanner/deep-eye/data/`) survive `docker compose down/up`
- Health: `GET /api/health -> {"status":"ok"}` (`api/main.py:23`) harus green di container

## Out of Scope (plans/SPEC.md:624)
- Modifikasi `scanner/deep-eye` engine, OAuth, mobile app, multi-user realtime

## Acceptance Criteria
- [ ] `docker compose up --build` → Web di `localhost` (mapped port) + API `/api/health` OK
- [ ] Reports & DB persist across restart
- [ ] Auth token required jika `DEEPEYE_AUTH_TOKEN` set, bypass jika unset (local dev)
- [ ] `docker compose config` valid, `.gitignore` tetap cover `data/*.db`

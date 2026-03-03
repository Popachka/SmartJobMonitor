# Production Deploy (VPS + Docker)

## Preconditions

- Docker and docker-compose are installed on the VPS.
- Repository is cloned on the VPS.
- `.env` exists on the server and is not committed to git.
- `MIRROR_CHANNEL` is an integer channel ID.

## Minimal `.env` checklist

- `APP_ENV=production`
- `API_ID`, `API_HASH`, `BOT_TOKEN`
- `GOOGLE_API_KEY`
- `MIRROR_CHANNEL` (int, for example `-1001234567890`)
- `POSTGRES_SERVER=db`
- `POSTGRES_PORT=5432`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `SENTRY_ENV=production`
- `LOGFIRE_ENV=production`
- `METRICS_ENABLED=true`

## First deployment

1. Pull code:
```bash
git pull --ff-only
```

2. Start only database:
```bash
make prod-db-up
```

3. Apply migrations:
```bash
make prod-migrate
```

4. Start application:
```bash
make prod-app-up
```

5. Check logs:
```bash
make prod-logs SERVICE=app
```

## Telethon first authorization

1. On first start, app may print QR login URL or QR code in logs.
2. Complete authorization once.
3. Restart app:
```bash
make prod-restart
```
4. Ensure no re-authorization is required. Session is stored in `telethon_session` volume.

## Regular release

1. Pull updates:
```bash
git pull --ff-only
```
2. Rebuild and restart:
```bash
make prod-up
```
3. Run migrations if schema changed:
```bash
make prod-migrate
```
4. Verify:
```bash
make prod-ps
make prod-logs SERVICE=app
```

## Health checks

- Bot responds to `/start`.
- Scraper receives and processes new channel messages.
- Metrics endpoint is available on `127.0.0.1:8000/metrics`.
- Sentry receives errors when `SENTRY_DSN` is configured.

## CI/CD deploy

### GitHub Secrets (Actions)

Add these repository secrets:

- `VPS_HOST` - server IP/domain.
- `VPS_PORT` - SSH port (`22` by default).
- `VPS_USER` - SSH user on VPS.
- `VPS_SSH_KEY` - private key for GitHub Actions.
- `VPS_APP_DIR` - absolute project path on VPS (for example `/root/apps/JobMonitor`).

### Workflow

- File: `.github/workflows/deploy-prod.yml`
- Trigger: manual (`Run workflow`).
- Deploy gate before SSH step: `uv run -m pytest -q`.
- Deploy transport: SSH (`appleboy/ssh-action`).
- Server deploy command: `make prod-deploy`.

### Run deploy from GitHub

1. Open `Actions` -> `Deploy Production`.
2. Click `Run workflow`.
3. Keep `ref=main` (or choose another branch/tag).
4. Wait for job to finish and verify server status in logs.

### Post-deploy checks

```bash
make prod-logs SERVICE=app
make prod-ps
```

- Verify bot responds to `/start`.
- Verify metrics endpoint `127.0.0.1:8000/metrics`.

## Pre-commit (local)

Before first commit, install hooks:

```bash
make precommit-install
```

Run hooks manually for all files:

```bash
make precommit-run
```

## Rollback

1. Checkout previous stable commit/tag:
```bash
git checkout <stable_tag_or_commit>
```
2. Rebuild and restart:
```bash
make prod-up
```
3. Review logs:
```bash
make prod-logs SERVICE=app
```

## Backup checklist (local Postgres in Docker)

- Run daily logical backup:
```bash
make prod-backup
```
- Optional custom backup path:
```bash
make prod-backup BACKUP_DIR=/var/backups/jobmonitor
```
- Store backups outside Docker volumes.
- Keep at least 7 daily and 4 weekly backups.

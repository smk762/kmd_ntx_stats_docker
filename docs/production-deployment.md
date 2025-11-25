# Production Deployment Guide

This guide covers the recommended approach for provisioning a new server, deploying `kmd_ntx_stats_docker`, and migrating the Postgres database.

## 1. Prerequisites

- Ubuntu 20.04+ (or distro with systemd, docker-ce, docker compose v2).
- Public DNS record pointing to the host if serving HTTPS.
- Non-root user with passwordless `sudo`.
- Firewall rules that allow SSH (22), HTTP/HTTPS (80/443), and any other published ports you enable locally (e.g., 8762, Komodo RPC if required).
- Access to the existing `.env` files (database credentials, Django secrets, API tokens).

## 2. Prepare the Server

1. Update packages and install tooling:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y ca-certificates curl gnupg git ufw
   ```
2. Install Docker Engine and docker compose <https://docs.docker.com/engine/install/ubuntu/>.
3. Add your deploy user to the `docker` group and log in again.
4. Configure UFW (or cloud firewall):
   ```bash
    sudo ufw allow OpenSSH
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw enable
   ```
5. (Optional) Install monitoring/metrics agents such as `node_exporter`, `promtail`, or your cloud provider tooling.

## 3. Clone and Configure the Application

```bash
git clone https://github.com/smk762/kmd_ntx_stats_docker.git
cd kmd_ntx_stats_docker
touch .env  # populate with the secrets from your secure store
```

Create or update `.env`, Django settings overrides, and any files referenced by `docker-compose.yml`. Set ownership for the Postgres data directory so the container can write to it:

```bash
mkdir -p postgres-data
sudo chown "$USER":"$USER" postgres-data -R
```

Build and start the stack:

```bash
docker compose build
docker compose up -d
```

Run Django migrations and collect static assets:

```bash
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic
docker compose run --rm web python manage.py createsuperuser
```

## 4. Database Migration Workflow

Prefer application-level dumps instead of copying the `postgres-data/` volume. The helper scripts wrap `pg_dump`/`psql`:

1. On the source host run `./util/export_postgres.sh /path/to/postgres.sql.gz`.
2. Transfer the dump to the new server via `scp`/`rsync`.
3. On the destination host run `./util/import_postgres.sh /path/to/postgres.sql.gz`.
4. Verify the application boots and key API endpoints work.

This approach is deterministic, version-agnostic, and easy to audit in backups (`backups/` is Git-ignored).

## 5. Web Server, TLS, and Static Assets

- Place NGINX (or your preferred reverse proxy) in front of the `web` container.
- Terminate TLS with Let's Encrypt (`certbot`) or a managed certificate and proxy to `127.0.0.1:8762`.
- Sync collected static files to `/var/www/stats.kmd.io/html/static` (already bind-mounted in `docker-compose.yml`).
- Enable gzip, caching headers, and request buffering at the proxy.

## 6. Operational Checklist

- **Backups**: automate `./util/export_postgres.sh` via cron, copy dumps off-host, and rotate older archives.
- **Monitoring**: watch container health (`docker compose ps`, `healthcheck.sh`), Postgres disk usage, and SSL expiry.
- **Logging**: ship logs from `/var/lib/docker/containers/*/*.log` or use `docker logs --follow <service>`.
- **Updates**: `git pull`, `docker compose build`, `docker compose up -d`, and rerun migrations after each release.
- **Security**: patch the host OS, rotate secrets regularly, and restrict SSH with keys + fail2ban.

## 7. Migration Strategy: New Image vs. Fresh Clone

For most deployments, cloning the repository on the destination host and wiring it to the imported database is preferred:

- Keeps source control history and configuration management transparent.
- Avoids shipping large custom Docker images that still require external volumes for Postgres/Komodo data.
- Simplifies upgrades because you rebuild locally with `docker compose build`.

Only consider crafting a bespoke migration image if you must freeze an entire environment (code + dependencies + data) for regulators or cannot rely on Git access. Even then, separate encrypted database dumps remain a better option for recovery.

## 8. Final Verification

1. Hit the public site/API endpoints and check for 200 responses.
2. Validate scheduled jobs/cron scripts (`code/scripts/cron_*`) are running if applicable.
3. Confirm SSL grade, DNS, and CDN (if any) are correct.
4. Document the deploy date, git commit, and dump filename for auditing.

Following this checklist ensures repeatable deployments and safer migrations across servers.


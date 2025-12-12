# Komodo Notarisation Stats (Docker)

Updated for Ubuntu 22.04.5 LTS and current stack.

## Host prerequisites
- Git, curl, build tools: `sudo apt update && sudo apt install -y git curl ca-certificates`
- Docker Engine + Compose plugin: https://docs.docker.com/engine/install/ubuntu/
  - After install: `sudo usermod -aG docker $USER` (relog) and `docker compose version`
- Python (for helpers): `sudo apt install -y python3 python3-venv`
- Optional: Nginx/Certbot if you front this with TLS (not required for local dev)
- KMD node (on host) with `~/.komodo/komodo.conf` or set `KMD_RPC_*` envs. RPC is locked to localhost and whitelisted read-only methods.
- MM2/KDF: provide `~/.kdf/MM2.json` or set `MM2_*` envs. KDF doc: [Configure MM2.json](https://komodoplatform.com/en/docs/komodo-defi-framework/setup/configure-mm2-json/).

## Quick start
```bash
git clone https://github.com/smk762/kmd_ntx_stats_docker
cd kmd_ntx_stats_docker

# Populate .env (prefills from ~/.komodo/komodo.conf and ~/.kdf/MM2.json)
python3 configure.py

# Build and start Postgres + web
docker compose up -d db
# (Optional) import an existing dump: cat stats-kmd-io-db.sql.gz | docker compose exec -T db bash -c "gunzip -c - | psql -U postgres postgres"
docker compose up -d web

# (Optional) expose via Cloudflare Tunnel instead of Nginx
# 1) In Cloudflare, create a tunnel and copy the token.
# 2) Add CLOUDFLARE_TUNNEL_TOKEN=<token> to .env
# 3) docker compose up -d cloudflared
# 4) In the Cloudflare dashboard, point the tunnel ingress to http://web:8762
#    and create/attach the DNS record for your hostname. Add Cloudflare Access if desired.
```
The app listens on `http://localhost:8762` (Postgres on 7654).

## Environment keys (summary)
- MM2_IP / MM2_PORT / MM2_USERPASS (prefilled from MM2.json if present)
- KMD_RPC_IP (forced to 127.0.0.1 if blank/0.0.0.0) / KMD_RPC_PORT (default 7771) / KMD_RPC_USERNAME / KMD_RPC_PASSWORD (prefilled from komodo.conf if present)
- POSTGRES_HOST/PORT/DB/USER/PASSWORD (defaults: db/5432/postgres/postgres/postgres)
- DJANGO_ALLOWED_HOSTS, SECRET_KEY, and the other keys added by `configure.py`

## Database ops
- Migrations: `docker compose run --rm web python manage.py migrate`
- Collect static: `docker compose run --rm web python manage.py collectstatic --noinput`
- Create superuser: `docker compose run --rm web python manage.py createsuperuser`
- Rebuild images after code changes: `docker compose build`

## Security notes
- KMD RPC is localhost-only; only whitelisted read-only methods are exposed (getblockcount, getaddresstxids, getrawtransaction, coinsupply). UI cannot issue write RPCs.
- Keep `.env` out of git; adjust file perms as needed.

## Maintenance
- Rebuild: `docker compose build`
- Restart: `docker compose up -d`
- Prune old images: `docker system prune -a --volumes`

## Backups / restore
- Export (example): `docker compose exec db pg_dump -U postgres postgres | gzip > backups/postgres-$(date +%s).sql.gz`
- Import (example): `cat path/to/dump.sql.gz | docker compose exec -T db bash -c "gunzip -c - | psql -U postgres postgres"`
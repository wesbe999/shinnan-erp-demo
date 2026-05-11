# Shinnan ERP Deployment Notes

## Runtime

- Python: `3.11.x`
- Install: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Required Persistent Paths

This project currently uses SQLite plus small JSON data files.

- `XUNNAN_DB_PATH`: SQLite database file path.
- `XUNNAN_DATA_DIR`: directory for JSON files such as notices and community data.

Local defaults:

- `XUNNAN_DB_PATH=./xunnan_dispatch.db`
- `XUNNAN_DATA_DIR=./data`

Server recommendation:

- `XUNNAN_DB_PATH=/var/data/xunnan_dispatch.db`
- `XUNNAN_DATA_DIR=/var/data/data`

On Render or another container host, mount `/var/data` as persistent storage before treating the server as production.

## Demo Data on Free Hosts

The repository includes `app/seed/demo_seed.sql` for demo-only deployments. When the configured SQLite database is empty, the app automatically imports this seed on startup.

- Disable this with `XUNNAN_AUTO_SEED_DEMO=0`.
- The seed is only used for empty SQLite databases.
- Existing databases with ticket data are not overwritten.

This is useful for Render free services because their local filesystem is not durable. It is not a replacement for production persistence.

## Before First Production Use

1. Upload or seed the intended `xunnan_dispatch.db`.
2. Confirm `/var/data` is persistent across deploys and restarts.
3. Set employee/admin PINs for real users.
4. Decide whether demo data should remain.
5. Run smoke tests for:
   - `/`
   - `/admin`
   - `/app/dispatch`
   - `/app/sales`
   - `/app/billing`
   - key APIs for dispatch, customers, sales, and billing.

## Backup

Back up these paths together:

- SQLite DB: value of `XUNNAN_DB_PATH`
- JSON data directory: value of `XUNNAN_DATA_DIR`

For SQLite, take backups while the app is stopped or use SQLite backup tooling to avoid partial copies.

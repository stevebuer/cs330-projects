# Quick Setup Checklist

## Before Running the Dashboard

- [ ] **Copy environment file**
  ```bash
  cp streamlit/.env.local streamlit/.env
  ```

- [ ] **Edit `.env` file** with your settings:
  - Database credentials (PGHOST, PGUSER, PGPASSWORD, etc.)
  - API URL (local or remote)

- [ ] **Create dashboard_users table**
  ```bash
  psql -d dx_analysis -f db_migrations/002_dashboard_users.sql
  ```

- [ ] **Install Python packages**
  ```bash
  pip install -r streamlit/requirements.txt
  ```

- [ ] **(Optional) Start local API** if using local data
  ```bash
  cd api && python dx_api.py
  ```

## Run the Dashboard

```bash
./run-dashboard-local.sh
```

Then open: **http://localhost:8501**

---

See `streamlit/LOCAL_DEVELOPMENT.md` for detailed documentation.

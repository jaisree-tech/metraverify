# MetraVerify — Digital Verification & Certification Platform

SIH26036 prototype: React frontend + Python (FastAPI) backend + SQLite/PostgreSQL database.

Covers Phase 1-4 of the MVP: registration/login with roles (USER, LMO officer, ADMIN),
instrument registration, verification applications, officer assignment, field
verification entry, digital certificate generation with QR code, and a public
QR verification page. A simple rule-based risk score (analytics) is also included.

**This version uses SQLite by default — no PostgreSQL install, no Docker needed.**
It's just a single file (`metraverify.db`) that gets created automatically. If you
want Postgres later (e.g. for Render deployment), see the "Optional: PostgreSQL"
section near the bottom.

---

## PLAN A — Run locally in 5 minutes (recommended for your mentor demo)

### 0. Install only these two things

1. **Python 3.10+** — https://www.python.org/downloads/ (tick "Add Python to PATH" while installing)
2. **Node.js 18+** — https://nodejs.org/ (LTS version)

That's it — no PostgreSQL, no Docker. Check they installed:
```
python --version
node --version
```

### 1. Unzip

Unzip `metraverify.zip` anywhere. You'll see:
```
metraverify/
  backend/
  frontend/
```
Open a terminal **inside the `metraverify` folder**.

### 2. Run the backend

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Windows:
copy .env.example .env
# Mac/Linux:
cp .env.example .env

python seed_admin.py
uvicorn app.main:app --reload --port 8000
```
You should see `Uvicorn running on http://127.0.0.1:8000`.
A file `metraverify.db` appears in the `backend` folder automatically — that's
your entire database, nothing to install.

Open http://localhost:8000/docs to confirm the API is alive (Swagger UI).
Keep this terminal running.

### 3. Run the frontend

Open a **second terminal**:
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**. Keep this terminal running too.

So during the demo you need exactly 2 terminals open (backend + frontend).

### 4. Demo flow to show your mentor

1. Register a normal user at http://localhost:5173/register
2. Login → **Instruments** → add a weighing machine
3. **Applications** → apply for verification
4. Logout → login as admin (`admin@metraverify.com` / `Admin@123`)
5. Register a second test account, go to **Admin** → promote it to "LMO Officer"
6. **Applications** (as admin) → assign the LMO officer to the application
7. Logout → login as that LMO officer → **Applications** → enter expected /
   observed / tolerance values → Submit Verification Result → if within
   tolerance, a certificate + QR code is auto-generated
8. Login back as the original user → **Certificates** → see the QR code
9. Go to http://localhost:5173/verify → paste the QR token shown in the
   certificate URL to see the public verification page (no login needed)

---

## PLAN B — Deploy live on Render (so you have a shareable link too)

Render can host both the backend and frontend for free. Push this project to a
GitHub repo first (Render deploys from GitHub), then:

### Backend (Web Service)
1. On https://render.com → **New +** → **Web Service** → connect your GitHub repo
2. Root directory: `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (Render dashboard → Environment):
   - `SECRET_KEY` = any long random string
   - (Optional, see below) `DATABASE_URL` if you want Postgres instead of SQLite
6. Deploy. Render gives you a URL like `https://metraverify-backend.onrender.com`
7. Visit `https://metraverify-backend.onrender.com/docs` to confirm it's live,
   then run the seed script once via Render's Shell tab: `python seed_admin.py`

Note: Render's free tier disk is not permanent across redeploys, so with SQLite
your data can reset when the service restarts. That's fine for a demo. For
something longer-lived, add Render's free managed PostgreSQL (see below).

### Frontend (Static Site)
1. On Render → **New +** → **Static Site** → same GitHub repo
2. Root directory: `frontend`
3. Build command: `npm install && npm run build`
4. Publish directory: `dist`
5. Add environment variable: `VITE_API_BASE_URL` = your backend URL from above
   (e.g. `https://metraverify-backend.onrender.com`)
6. Deploy. Render gives you a URL like `https://metraverify.onrender.com` — this
   is the link you show your mentor.

### Optional: PostgreSQL instead of SQLite (for Render)
1. Render → **New +** → **PostgreSQL** (free tier) → copy the "Internal Database URL"
2. In your backend Web Service → Environment → set `DATABASE_URL` to that value
3. Redeploy the backend — it will automatically create all tables in Postgres
   on startup (same code, nothing else changes)

---

## Project structure

```
backend/
  app/
    main.py                FastAPI app entrypoint
    models.py               Database tables (SQLAlchemy)
    schemas.py                Request/response shapes (Pydantic)
    auth.py                     Login, JWT tokens, password hashing
    routers/
      auth_router.py               /auth/register, /auth/login, /auth/me
      instruments_router.py        /instruments
      applications_router.py       /applications
      verification_router.py       /verification (officer submits results)
      certificates_router.py       /certificates (+ public QR verify)
      admin_router.py              /admin (user management)
      analytics_router.py          /analytics (dashboard counts, risk score)
  seed_admin.py            run once to create the default admin login
  requirements.txt
  .env.example

frontend/
  src/
    pages/                one file per screen
    components/             Navbar, ProtectedRoute
    api.js                    axios client (reads VITE_API_BASE_URL)
    AuthContext.jsx             stores logged-in user + JWT token
  .env.example

docker-compose.yml      optional — only needed if you want Postgres locally
```

---

## Notes for your presentation

- Roles: **USER** (shop owner), **LMO** (inspection officer), **ADMIN**. The
  "PUBLIC" role isn't a login — it's just the QR verification page anyone can open.
- Database tables map directly to the ones suggested in the problem statement:
  `users`, `instruments`, `applications`, `verifications`, `certificates`.
- The risk score (`/analytics/risk-score/{instrument_id}`) is intentionally
  rule-based (failures, instrument age, deviation history) — matches the
  "MVP doesn't need ML yet" recommendation. Mention in your report that a
  supervised ML model (Random Forest / XGBoost) is future scope.
- QR codes don't store certificate data directly — they store a random
  `qr_token` that the backend looks up, the safer approach.

## What's intentionally left out of this MVP (future work)

- Document/photo upload (Module 10) and OCR
- Real email/SMS notifications (the in-app notification table exists in the
  schema; wiring it up is a good next feature for a team member to add)
- Automatic officer allocation based on location/workload
- GIS heatmaps, anomaly detection, ML failure prediction

## Optional: PostgreSQL for local development (instead of SQLite)

If your team later wants Postgres locally instead of SQLite, install Docker
Desktop, then:
```bash
docker compose up -d
```
And change `DATABASE_URL` in `backend/.env` to:
```
DATABASE_URL=postgresql://metra_user:metra_pass@localhost:5432/metraverify
```
Nothing else changes — the same backend code works with either database.

## Troubleshooting

- **`uvicorn` command not found** → make sure the virtual environment is
  activated (you should see `(venv)` at the start of your terminal line).
- **Frontend shows network errors** → make sure the backend terminal is still
  running on port 8000.
- **Port already in use** → close any old `uvicorn`/`npm run dev` terminal
  still running from before, or change the port number.
- **CORS errors in browser console** → shouldn't happen (CORS is fully open in
  `main.py` for development); if using Render, double check `VITE_API_BASE_URL`
  points to the correct backend URL with no trailing slash.

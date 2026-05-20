# Tour Cost Calculator — Railway Deployment Guide

## Project structure
```
tour_app/
├── app.py            ← Flask app (auto-creates DB tables on startup)
├── Procfile          ← tells Railway how to start the app
├── requirements.txt  ← flask + gunicorn + mysql-connector-python
├── runtime.txt       ← Python 3.11
├── nixpacks.toml     ← Railway build config
└── templates/
    └── index.html
```

---

## Deploy in 5 steps

### Step 1 — Push to GitHub
Create a new GitHub repo and push all these files to it.

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOURUSERNAME/tour-app.git
git push -u origin main
```

---

### Step 2 — Create a Railway project

1. Go to **https://railway.app** and log in
2. Click **"New Project"**
3. Choose **"Deploy from GitHub repo"**
4. Select your repo → Railway will detect it and start building

---

### Step 3 — Add a MySQL database

1. In your Railway project dashboard, click **"+ New"**
2. Choose **"Database"** → **"Add MySQL"**
3. Railway creates a MySQL instance and automatically sets these
   environment variables in your project:
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

Your `app.py` already reads all of these — **no manual config needed**.

---

### Step 4 — Link the MySQL variables to your web service

1. Click on your **web service** (the Flask app) in the project dashboard
2. Go to **Variables** tab
3. Click **"+ Add Reference"** → select the MySQL service
4. This shares all `MYSQL*` variables with your Flask app automatically

---

### Step 5 — Redeploy

1. Go to the **Deployments** tab of your web service
2. Click **"Redeploy"** (or push a new commit — Railway auto-deploys)
3. Watch the build logs — you should see `Database tables ready.`
4. Click the generated domain (e.g. `tour-app-production.up.railway.app`)

Your app is live! ✓

---

## Environment variables (set automatically by Railway MySQL plugin)

| Variable | Example value |
|----------|--------------|
| MYSQLHOST | containers-us-west-1.railway.app |
| MYSQLPORT | 6539 |
| MYSQLUSER | root |
| MYSQLPASSWORD | (auto-generated) |
| MYSQLDATABASE | railway |

You never need to set these manually — Railway injects them.

---

## Troubleshooting

**Build fails — "No module named gunicorn"**
Make sure `gunicorn` is in `requirements.txt` and redeploy.

**"Can't connect to MySQL server"**
Check that you added the MySQL service reference to your web service's
Variables tab (Step 4). Without this link, MYSQL* vars won't be available.

**App crashes on startup**
Click the deployment → View logs. The most common cause is the DB not
being ready yet on first deploy. Click "Redeploy" once — it will work
on the second attempt after MySQL is fully provisioned.

**Tables not created**
`app.py` calls `init_db()` automatically at startup via `app_context`.
Check deploy logs for `Database tables ready.` — if you see a warning
instead, the DB connection vars may not be linked yet.

---

## Notes

- Railway's free Hobby plan gives $5/month in credits — enough for a
  small app running 24/7 for about a month.
- The app uses `gunicorn` (not Flask's dev server) for production.
- Tables are created automatically — no need to run schema.sql manually.
- `PORT` is injected by Railway; `app.py` reads it with `os.environ.get("PORT", 5000)`.

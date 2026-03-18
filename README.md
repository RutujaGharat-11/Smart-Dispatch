# 🚀 SmartDispatch

SmartDispatch is a role-based public resource scheduling platform with:
- **Next.js (App Router)** frontend
- **Flask + SQLite** backend

Users can submit requests and track their own request status. Admins can monitor requests, manage resource availability, and run scheduling operations.

---

## ✨ Features

- Role-based login (`USER` / `ADMIN`)
- Session-based authentication (Flask sessions with cookies)
- Request submission workflow for users
- Admin dashboard with requests/resources/assignments
- Manage Resources page with status controls
- Scheduler trigger endpoint

---

## 🛠 Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Bootstrap UI classes in selected pages
- **Backend:** Flask, SQLite, Flask-CORS, Werkzeug password hashing

---

## 📁 Project Structure (current)

```text
app.py
auth.py
database.py
schema.sql

app/
  layout.tsx
  page.tsx
  login/page.jsx
  signup/page.jsx
  create-account/page.jsx
  request/page.tsx
  dashboard/page.tsx
  manage-resources/page.tsx
  user-dashboard/page.tsx

components/
  navbar.tsx
  dashboard/*
  request/*
  home/*
```

---

## 👥 Roles

### USER
- Create account
- Login as USER
- Submit request
- View personal requests on User Dashboard

### ADMIN
- Login as ADMIN
- View admin dashboard
- Manage resources (`Available` / `Unavailable`)
- Run scheduler

---

## ▶️ Run Locally

### 1) Backend (Flask)

```bash
# from project root
python -m venv .venv
.venv\Scripts\activate
pip install flask flask-cors werkzeug
python app.py
```

Backend runs at: `http://localhost:5000`

### 2) Frontend (Next.js)

```bash
# from project root
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## 🔐 Auth Notes

- Frontend uses same-origin `/api/*` calls by default.
- Next.js rewrites `/api/:path*` to backend URL from `BACKEND_URL` (or `NEXT_PUBLIC_API_URL`) in `next.config.mjs`.
- For Vercel deployment, set `BACKEND_URL=https://<your-render-service>.onrender.com`.
- For Render deployment, set `FRONTEND_URL=https://<your-vercel-domain>.vercel.app` (or comma-separated domains).
- For cross-site cookies on Render, ensure `SESSION_COOKIE_SAMESITE=None` and `SESSION_COOKIE_SECURE=True`.
- Login endpoint: `/api/login`
- Check session endpoint: `/api/check-auth`
- Logout endpoint: `/api/logout`

---

## 🌿 Git Workflow for This Repo

This local folder is connected to:

`https://github.com/RutujaGharat-11/Smart-Dispatch`

Use this standard flow:

```bash
git add .
git commit -m "your message"
git push
```

---

## 📌 Branch

- Default working branch is `main`.


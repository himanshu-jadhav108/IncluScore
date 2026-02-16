# IncluScore — Deployment Guide

## Backend → Render

### 1. Create `render.yaml` (already included)

```yaml
services:
  - type: web
    name: incluscore-api
    runtime: python
    buildCommand: pip install -r requirements.txt && python train_model.py
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: ENV
        value: production
```

### 2. Deploy to Render

1. Go to [render.com](https://render.com) and sign up
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set root directory to `backend/`
5. Add environment variables in the Render dashboard:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase anon key
6. Click **Deploy**

Your API will be live at `https://incluscore-api.onrender.com`

### 3. Update Frontend API URL

In `frontend/index.html`, change:
```javascript
const API_URL = 'http://localhost:8000';
```
to:
```javascript
const API_URL = 'https://incluscore-api.onrender.com';
```

---

## Frontend → Vercel

### 1. Create `vercel.json`

```json
{
  "version": 2,
  "builds": [
    { "src": "frontend/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/frontend/$1" }
  ]
}
```

### 2. Deploy via Vercel CLI

```bash
npm install -g vercel
vercel deploy
```

Or connect your GitHub repo at [vercel.com](https://vercel.com) for automatic deployments.

---

## Frontend → Netlify (Alternative)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy from frontend directory
cd frontend
netlify deploy --prod --dir .
```

---

## Database → Supabase

1. Go to [supabase.com](https://supabase.com) and create a project
2. Open the **SQL Editor**
3. Paste and run the contents of `database/schema.sql`
4. Copy your **Project URL** and **anon key** from Settings → API
5. Add them as environment variables in your Render service

---

## Full Deployment Checklist

- [ ] Supabase project created and schema applied
- [ ] ML model trained (`python train_model.py`)
- [ ] Backend deployed on Render with env vars set
- [ ] `API_URL` in frontend updated to Render URL
- [ ] Frontend deployed on Vercel/Netlify
- [ ] Health check: `GET https://your-api.onrender.com/` returns `{"status":"healthy"}`
- [ ] End-to-end test: Select persona → verify score loads
- [ ] Simulate transaction: verify score updates

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Optional | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Optional | Supabase anon or service role key |
| `ENV` | No | `development` or `production` |

> **Note:** The app runs fully offline with mock data if Supabase is not configured.

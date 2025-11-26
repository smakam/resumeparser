# Railway Deployment Guide

**Note**: Railway no longer offers a free tier. For free hosting, see `DEPLOYMENT.md` for Render + Vercel option.

Deploy both frontend and backend on Railway in one project (paid tier required).

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended for easy repo connection)
3. Click "New Project"

## Step 2: Deploy from GitHub

1. Click "Deploy from GitHub repo"
2. Select your repository: `smakam/resumeparser`
3. Railway will auto-detect the project

## Step 3: Configure Backend Service

Railway will create a service automatically. Configure it:

1. **Settings → Deploy**

   - **Root Directory**: Leave empty (project root)
   - **Build Command**: `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Settings → Environment Variables**
   - Add: `OPENAI_API_KEY` = your OpenAI API key
   - Add: `ALLOWED_ORIGINS` = `*` (or your Railway frontend URL after deployment)
   - Railway automatically sets `PORT`

## Step 4: Add Static Files Service (Frontend)

1. Click "+ New" → "Static Files"
2. **Root Directory**: `frontend/dist`
3. Railway will serve the built frontend

## Step 5: Configure Frontend Environment

1. Go to Static Files service → Settings → Environment Variables
2. Add: `VITE_API_URL` = your Railway backend service URL
   - Find this in: Backend service → Settings → Domains
   - Example: `https://resume-parser-backend-production.up.railway.app`

## Step 6: Update CORS (After Getting URLs)

1. Once both services are deployed, note their URLs
2. Go to Backend service → Settings → Environment Variables
3. Update `ALLOWED_ORIGINS` with your frontend URL:
   - Example: `https://resume-parser-frontend-production.up.railway.app`

## Alternative: Single Service with Custom Start Script

If you prefer one service, create a `start.sh` script:

```bash
#!/bin/bash
# Start backend in background
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT &
# Serve frontend
cd frontend/dist && python -m http.server 3000
```

## Environment Variables Summary

### Backend Service

- `OPENAI_API_KEY` - Your OpenAI API key
- `ALLOWED_ORIGINS` - Frontend URL (or `*` for all)
- `PORT` - Auto-set by Railway

### Frontend Service (Static Files)

- `VITE_API_URL` - Backend service URL

## Troubleshooting

- **Build fails**: Check Railway logs for Python/Node version issues
- **CORS errors**: Update `ALLOWED_ORIGINS` with exact frontend URL
- **Frontend can't reach backend**: Check `VITE_API_URL` is set correctly
- **Port conflicts**: Railway sets `$PORT` automatically, don't hardcode

## Railway Free Tier Limits

- $5 credit per month
- Services sleep after inactivity
- Generous bandwidth limits
- Perfect for development/testing

## After Deployment

1. Visit your frontend URL
2. Test resume upload
3. Check Railway logs if issues occur
4. Monitor usage in Railway dashboard

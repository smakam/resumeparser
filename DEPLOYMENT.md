# Deployment Guide - Free Tier Hosting

This guide covers deploying the Resume Parser to free tier hosting providers.

## Option 1: Render.com (Recommended)

### Backend Deployment

1. **Create Render Account**

   - Go to [render.com](https://render.com) and sign up (free tier available)

2. **Create New Web Service**

   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Or use the `render.yaml` file for automatic setup

3. **Configure Backend Service**

   - **Name**: `resume-parser-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: Leave empty (or set to project root)

4. **Set Environment Variables**

   - Go to "Environment" tab
   - Add: `OPENAI_API_KEY` = your OpenAI API key
   - Render automatically sets `PORT` variable

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Note the URL (e.g., `https://resume-parser-backend.onrender.com`)

### Frontend Deployment

1. **Build Frontend**

   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy to Vercel (Free)**

   - Go to [vercel.com](https://vercel.com) and sign up
   - Import your GitHub repository
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Configure Environment Variables**

   - Add: `VITE_API_URL` = your Render backend URL (e.g., `https://resume-parser-backend.onrender.com`)

4. **Update Frontend API URL**
   - Update `frontend/vite.config.js` to use environment variable for API proxy

## Option 2: Railway.app (Alternative)

### Backend

1. Sign up at [railway.app](https://railway.app)
2. Create new project from GitHub
3. Add Python service
4. Set environment variables
5. Railway auto-detects FastAPI and deploys

### Frontend

1. Add static site service
2. Point to `frontend/dist` after build
3. Set environment variables

## Option 3: Fly.io (Alternative)

### Backend

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Initialize: `fly launch` in project root
4. Set secrets: `fly secrets set OPENAI_API_KEY=your_key`
5. Deploy: `fly deploy`

## Quick Start with Render

1. **Backend**:

   ```bash
   # Push code to GitHub
   git add .
   git commit -m "Ready for deployment"
   git push

   # Then use Render dashboard to connect repo
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm run build
   # Deploy dist/ folder to Vercel or Netlify
   ```

## Environment Variables Needed

### Backend

- `OPENAI_API_KEY`: Your OpenAI API key

### Frontend (if using separate deployment)

- `VITE_API_URL`: Backend API URL

## Notes

- Render free tier: Services sleep after 15 minutes of inactivity (first request may be slow)
- Vercel free tier: Generous limits, no sleeping
- Consider upgrading to paid tier for production use
- Monitor API usage to avoid exceeding OpenAI quotas

## Troubleshooting

- **Backend not starting**: Check logs in Render dashboard
- **CORS errors**: Ensure backend CORS allows your frontend domain
- **API timeouts**: Render free tier has timeout limits, consider upgrading
- **Build failures**: Check Python version (3.12 recommended)

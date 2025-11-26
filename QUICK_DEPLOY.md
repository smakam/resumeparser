# Quick Deployment Guide

## Step 1: Prepare Your Code

1. **Remove Gemini dependencies** (already done)
2. **Commit to GitHub**:
   ```bash
   git add .
   git commit -m "Remove Gemini, ready for deployment"
   git push origin main
   ```

## Step 2: Deploy Backend to Render.com

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `resume-parser-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. Copy your backend URL (e.g., `https://resume-parser-backend.onrender.com`)

## Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - Key: `VITE_API_URL`
   - Value: Your Render backend URL (from Step 2)
6. Click "Deploy"
7. Wait for deployment (2-3 minutes)
8. Your app is live! 🎉

## Alternative: Deploy Both to Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Create new project from GitHub
3. Add two services:
   - **Backend**: Python service, set start command to `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Frontend**: Static site, point to `frontend/dist` after build
4. Set environment variables for both
5. Deploy!

## Important Notes

- **Render free tier**: Services sleep after 15 min inactivity (first request may be slow)
- **Vercel free tier**: No sleeping, generous limits
- **CORS**: Backend CORS is configured to allow your frontend domain
- **API Keys**: Never commit API keys to GitHub - use environment variables

## Testing After Deployment

1. Visit your Vercel frontend URL
2. Upload a test resume
3. Check that both GPT-4o and GPT-5.1 models work
4. Verify results display correctly

## Troubleshooting

- **Backend 500 errors**: Check Render logs for API key issues
- **CORS errors**: Update `ALLOWED_ORIGINS` in backend environment variables
- **Slow first request**: Normal on Render free tier (service waking up)
- **Build failures**: Check Python version (3.12) and Node version (18+)


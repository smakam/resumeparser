# Free Tier Deployment Guide

Railway no longer offers a free tier. Here are the best **FREE** options:

## 🏆 Best Option: Render for Both (Simplest)

**Why**:

- ✅ **Simplest setup** - Everything in one place
- ✅ **One dashboard** - Easy to manage
- ✅ **Free tier** - Both services free
- ⏰ Both services sleep after 15 min (first request may be slow, but acceptable for most use cases)

### Deploy Both on Render

1. **Backend Service**:

   - Go to [render.com](https://render.com) → Sign up
   - **New** → **Web Service**
   - Connect GitHub → Select `smakam/resumeparser`
   - **Configure**:
     - **Name**: `resume-parser-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `OPENAI_API_KEY` = your OpenAI key
     - `ALLOWED_ORIGINS` = `*` (or your frontend URL after deployment)
   - **Deploy** → Copy backend URL

2. **Frontend Service**:
   - **New** → **Static Site**
   - Connect same GitHub repo
   - **Configure**:
     - **Name**: `resume-parser-frontend`
     - **Build Command**: `cd frontend && npm install && npm run build`
     - **Publish Directory**: `frontend/dist`
   - **Environment Variables**:
     - `VITE_API_URL` = your backend URL (from step 1)
   - **Deploy** → Your app is live! 🎉

**Note**: First request after inactivity may take 10-30 seconds (service waking up), but subsequent requests are fast.

---

## Option 2: Render + Vercel (Fastest Frontend)

**Why**:

- Render: Free backend hosting (sleeps after 15 min inactivity)
- Vercel: Free frontend hosting (no sleeping, fast CDN)
- Best user experience (frontend always fast)

### Backend on Render (Free)

1. **Sign up** at [render.com](https://render.com)
2. **New** → **Web Service**
3. **Connect GitHub** → Select `smakam/resumeparser`
4. **Configure**:
   - **Name**: `resume-parser-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   - `OPENAI_API_KEY` = your OpenAI key
   - `ALLOWED_ORIGINS` = `*` (or your Vercel URL after deployment)
6. **Deploy** → Copy your backend URL

### Frontend on Vercel (Free)

1. **Sign up** at [vercel.com](https://vercel.com)
2. **Add New** → **Project**
3. **Import** `smakam/resumeparser`
4. **Configure**:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. **Environment Variables**:
   - `VITE_API_URL` = your Render backend URL
6. **Deploy** → Your app is live! 🎉

**Note**: First request to Render backend may be slow (service waking up)

---

## Option 3: Fly.io (Free Tier Available)

**Why**:

- Free tier: 3 shared VMs, 3GB storage, 160GB bandwidth
- Global edge network
- No sleeping

### Setup

1. **Install Fly CLI**:

   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:

   ```bash
   fly auth login
   ```

3. **Initialize** (in project root):

   ```bash
   fly launch
   ```

4. **Set secrets**:

   ```bash
   fly secrets set OPENAI_API_KEY=your_key
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

**Note**: You'll need to create a `fly.toml` file. See Fly.io docs for full-stack app setup.

---

## Option 4: Cyclic (Free Tier)

**Why**:

- Free tier: 10,000 API requests/month
- Serverless architecture
- Fast cold starts

### Setup

1. Sign up at [cyclic.sh](https://cyclic.sh)
2. Connect GitHub repo
3. Cyclic auto-detects and deploys
4. Set environment variables in dashboard

**Note**: Better for serverless functions, may need adjustments for FastAPI

---

## Comparison Table

| Provider    | Free Tier | Sleeps?         | Best For        |
| ----------- | --------- | --------------- | --------------- |
| **Render**  | ✅ Yes    | ⏰ Yes (15 min) | Backend APIs    |
| **Vercel**  | ✅ Yes    | ❌ No           | Frontend/Static |
| **Fly.io**  | ✅ Yes    | ❌ No           | Full-stack apps |
| **Cyclic**  | ✅ Yes    | ⏰ Yes          | Serverless      |
| **Railway** | ❌ No     | N/A             | Paid only       |

---

## Quick Comparison

### Render for Both (Recommended for Simplicity)

- ✅ Simplest setup (one platform)
- ✅ Easy management
- ⏰ Both sleep after 15 min (acceptable for most projects)
- **Best for**: Personal projects, MVPs, demos

### Render + Vercel (Recommended for Performance)

- ✅ Frontend never sleeps (always fast)
- ✅ Better user experience
- ⚠️ Two platforms to manage
- **Best for**: Production apps, high-traffic sites

---

## Environment Variables Summary

### Backend (Render)

- `OPENAI_API_KEY` - Your OpenAI API key
- `ALLOWED_ORIGINS` - `*` or your Vercel URL

### Frontend (Vercel)

- `VITE_API_URL` - Your Render backend URL

---

## Troubleshooting

- **Render slow first request**: Normal (service waking up)
- **CORS errors**: Update `ALLOWED_ORIGINS` in Render
- **Build failures**: Check Python 3.12 and Node 18+
- **API timeouts**: Render free tier has 30s timeout limit

---

## Cost Comparison

- **Render + Vercel**: $0/month (free tier)
- **Fly.io**: $0/month (free tier, limited resources)
- **Railway**: ~$5-20/month (no free tier)

**Recommendation**: Start with Render + Vercel, upgrade if needed!

# Deploying VC Copilot

This guide explains how to deploy the VC Copilot application with the backend on Railway and the frontend on Vercel.

## Backend Deployment (Railway)

### Prerequisites
- A [Railway](https://railway.app/) account
- A [GitHub](https://github.com/) account (for connecting your repository)

### Steps

1. **Push your code to GitHub**
   - Create a new repository on GitHub
   - Push your local code to the repository

2. **Create a new project on Railway**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select your repository

3. **Add a PostgreSQL database**
   - In your Railway project, click "New"
   - Select "Database" → "PostgreSQL"
   - This will create a new PostgreSQL instance

4. **Configure environment variables**
   - In your Railway project, go to the "Variables" tab
   - Add the following variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `DATABASE_URL`: This should be automatically linked from your PostgreSQL service

5. **Deploy your application**
   - Railway will automatically deploy your application
   - You can monitor the deployment in the "Deployments" tab

6. **Get your API URL**
   - Once deployed, go to the "Settings" tab
   - Find your deployment domain (e.g., `https://vc-copilot-production.up.railway.app`)
   - This is your backend API URL

## Frontend Deployment (Vercel)

### Prerequisites
- A [Vercel](https://vercel.com/) account
- Your backend API URL from Railway

### Steps

1. **Create a new project on Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New" → "Project"
   - Import your GitHub repository

2. **Configure environment variables**
   - In the project settings, go to "Environment Variables"
   - Add `NEXT_PUBLIC_API_URL` with your Railway backend URL

3. **Deploy your application**
   - Click "Deploy"
   - Vercel will build and deploy your Next.js application

4. **Access your application**
   - Once deployed, Vercel will provide you with a URL
   - You can also configure a custom domain in the project settings

## Configuration Files

We've added several configuration files to make deployment easier:

1. **`Procfile`**: Tells Railway how to run your FastAPI application
2. **`railway.json`**: Configures deployment settings for Railway
3. **`.env.production.example`**: Template for frontend environment variables

## Database Integration

The application now uses a PostgreSQL database instead of in-memory storage:

1. **Models**: Defined in `backend/models.py`
2. **Database Operations**: Implemented in `backend/database.py`
3. **API Integration**: Updated in `backend/main.py`

## Local Development

You can still run the application locally:

### Backend
```bash
cd /path/to/VC-Copilot
python run_backend.py
```

### Frontend
```bash
cd /path/to/VC-Copilot/frontend
npm run dev
```

## Troubleshooting

### CORS Issues
If you encounter CORS issues:
1. Make sure your backend CORS configuration includes your Vercel domain
2. Update the `allow_origins` list in `backend/main.py`
3. Redeploy your backend

### Database Connection Issues
If your application can't connect to the database:
1. Check the `DATABASE_URL` environment variable in Railway
2. Make sure your application is properly configured to use the database
3. Check the Railway logs for any connection errors

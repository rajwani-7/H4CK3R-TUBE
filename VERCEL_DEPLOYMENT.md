# Vercel Deployment Guide

This guide will help you deploy your YouTube Downloader application to Vercel.

## Important Notes about Vercel Deployment

1. **Serverless Limitations**: Vercel runs on serverless functions which have important limitations:
   - No filesystem access for writing files (downloads won't work)
   - Limited execution time (max 10 seconds for hobby plan)
   - Limited memory (max 1GB on hobby plan)

2. **Functionality in Vercel**: The application on Vercel will:
   - Show video information
   - Provide commands for local downloading
   - Cannot actually download videos (this is by design)

## Deployment Steps

### 1. Install Vercel CLI

If you haven't already, install the Vercel CLI:

```
npm install -g vercel
```

### 2. Login to Vercel

Run the login command:

```
vercel login
```

Follow the prompts to complete the login process.

### 3. Deploy Your Project

1. Navigate to your project directory
2. Run:

```
vercel
```

3. Answer the prompts:
   - Set up and deploy? **Yes**
   - Which scope? **(Select your account)**
   - Link to existing project? **No**
   - What's your project name? **(Enter a name)**
   - In which directory is your code located? **./  (root directory)**
   - Want to override settings? **No**

### 4. Troubleshooting 

If you encounter a 500 error:

1. Check the deployment logs:
```
vercel logs your-project-name
```

2. Visit the diagnostic endpoints:
   - `/api/health-check` - Checks if the API is running
   - `/api/debug` - Shows detailed information about file paths
   - `/api/static-html` - A simple HTML page served directly by the API

3. Common issues:
   - Flask can't find templates: Make sure templates are included in the build
   - CORS issues: The browser might block requests to your API
   - Memory limits: yt-dlp might use too much memory for some operations

### 5. Application Limitations

Remember that on Vercel:
- You can get video information
- You cannot download videos (this requires file system writes)
- You should use the commands provided to download locally

## Local Development

To run locally with full functionality:

```
python app.py
```

This will give you the full application with download capabilities.

## Need Help?

If you continue to encounter issues, try:

1. Check the Vercel logs for specific error messages
2. Visit `/api/debug` on your deployed application to see configuration details
3. Simplify your application by removing complex features temporarily 
# Deployment Guide for GitHub Pages

This guide will help you deploy the USIS CDN system to GitHub Pages.

## Prerequisites

- Git installed on your system
- A GitHub account
- The project files ready to deploy

## Step-by-Step Deployment

### 1. Initialize Git Repository (if not already done)

```bash
cd /path/to/usis-cdn
git init
```

### 2. Add All Files to Git

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: USIS CDN system"
```

### 4. Create GitHub Repository

1. Go to https://github.com/new
2. Enter repository name: `usis-cdn` (or any name you prefer)
3. Set visibility to **Public** (required for GitHub Pages)
4. **Do NOT** initialize with README, .gitignore, or license
5. Click **Create repository**

### 5. Link Local Repository to GitHub

Replace `YOUR-USERNAME` with your actual GitHub username:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/usis-cdn.git
git push -u origin main
```

### 6. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top navigation)
3. Scroll down and click **Pages** (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**
6. Wait 1-2 minutes for deployment

### 7. Access Your Live Site

Your site will be available at:
```
https://YOUR-USERNAME.github.io/usis-cdn/
```

### API Endpoints

Once deployed, your API endpoints will be:
- **Connect API**: `https://YOUR-USERNAME.github.io/usis-cdn/connect.json`
- **Exams API**: `https://YOUR-USERNAME.github.io/usis-cdn/exams.json`

## Automated Updates

The GitHub Actions workflow (`.github/workflows/update-data.yml`) is already configured to:
- Run daily at 6 AM UTC (12 PM Bangladesh Time)
- Automatically fetch fresh data
- Commit and push updates

### Manual Trigger

To manually trigger an update:
1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Update USIS Data** workflow
4. Click **Run workflow**
5. Click the green **Run workflow** button

## Verifying Deployment

1. Visit `https://YOUR-USERNAME.github.io/usis-cdn/`
2. Check that the metadata statistics are displayed
3. Test the download buttons
4. Verify the API endpoints return JSON data

## Troubleshooting

### Pages Not Working
- Ensure the repository is public
- Check that GitHub Pages is enabled in Settings
- Wait a few minutes for the initial deployment

### Actions Not Running
- Go to Settings > Actions > General
- Ensure "Allow all actions" is selected
- Check that workflows have write permissions

### Data Not Updating
- Check the Actions tab for workflow run history
- Review logs if any workflow failed
- Ensure the source API is accessible

## Updating the Code

To update your deployment after making changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

GitHub Pages will automatically redeploy within 1-2 minutes.

## Custom Domain (Optional)

If you have a custom domain:
1. Go to Settings > Pages
2. Enter your domain in "Custom domain"
3. Follow GitHub's instructions to configure DNS

---

**Need help?** Check the main `README.md` or open an issue on GitHub.

# GitHub Actions Deployment Workflows

This directory contains GitHub Actions workflows for deploying the backend and frontend to Vercel.

## Required GitHub Secrets

Before these workflows can run successfully, you need to configure the following secrets in your GitHub repository settings:

### 1. `VERCELTOKEN`
Your Vercel authentication token. You can obtain this from:
- Go to [Vercel Account Settings](https://vercel.com/account/tokens)
- Click "Create Token"
- Give it a descriptive name (e.g., "GitHub Actions")
- Copy the token and add it as a GitHub secret

### 2. `VERCEL_ORG_ID`
Your Vercel organization ID. To find this:
- Install Vercel CLI locally: `npm i -g vercel`
- Run `vercel login` to authenticate
- Navigate to your project directory
- Run `vercel link` to link your project
- The `.vercel/project.json` file will contain your `orgId`

### 3. `VERCEL_PROJECT_ID_BACKEND`
The Vercel project ID for your backend. To find this:
- After linking your backend project with `vercel link`
- Check `.vercel/project.json` in your backend directory
- Use the `projectId` value

### 4. `VERCEL_PROJECT_ID_FRONTEND`
The Vercel project ID for your frontend (when you create it). Follow the same process as above but for your frontend project.

## How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with its corresponding value

## Workflow Descriptions

### `deploy-backend.yml`
- Triggers on:
  - Push to `main` branch when backend files change
  - Pull requests affecting backend files
  - Manual trigger (workflow_dispatch)
- Deploys to production on `main` branch pushes
- Creates preview deployments for pull requests

### `deploy-frontend.yml`
- Same trigger conditions as backend but for frontend files
- Ready to use when you set up your frontend Vercel project

## Usage

Once all secrets are configured:
1. Any push to `main` that modifies backend files will automatically deploy to production
2. Pull requests will create preview deployments and comment the URL on the PR
3. You can manually trigger deployments from the Actions tab

## Notes

- The workflows use path filters to only run when relevant files change
- Preview deployments are automatically created for pull requests
- The workflows will comment preview URLs on pull requests for easy testing
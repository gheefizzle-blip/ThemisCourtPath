# Google Cloud Platform Setup Guide — Themis Court Path
## DRAFT — REQUIRES COMMANDER REVIEW
**Date**: 2026-04-17
**Work Order**: TCP-WO-003
**For**: Commander Gary Spear (step-by-step, beginner-friendly)

---

## What We're Doing

Setting up a Google Cloud account and project so we can deploy the Themis Court Path Python application to the internet. The app will run on **Google Cloud Run** — a service that runs your app in a container and only charges you when someone is actually using it.

**Estimated time**: 30-45 minutes
**Cost**: Free for our usage level (Phase 1)

---

## Section 1: Create Google Cloud Account

1. Open Chrome and go to: **https://console.cloud.google.com**
2. Sign in with your Google account (use the same one you use for Gmail)
3. If you've never used Google Cloud, you'll see a "Welcome" screen
4. You may need to agree to Terms of Service
5. Google offers a **$300 free credit** for new accounts — accept it if offered
6. You'll need to add a credit card, but **you will NOT be charged** unless you exceed the free tier (which we won't for a long time)

---

## Section 2: Create a New Project

1. At the top of the Google Cloud Console, you'll see a project dropdown (might say "Select a project" or show an existing project name)
2. Click that dropdown
3. Click **"NEW PROJECT"** (top right of the popup)
4. Fill in:
   - **Project name**: `Themis Court Path`
   - **Project ID**: It will auto-generate one like `themis-court-path-12345`. You can edit this to just `themis-court-path` if available
   - **Location**: Leave as "No organization"
5. Click **CREATE**
6. Wait 10-15 seconds for it to create
7. Make sure the new project is selected in the top dropdown

---

## Section 3: Enable Required APIs

APIs are like switches that turn on different Google Cloud features. We need to flip a few on.

1. In the left sidebar, click **"APIs & Services"** → **"Library"**
2. Search for and enable each of these (click on each, then click **"ENABLE"**):

| API | What It Does |
|-----|-------------|
| **Cloud Run API** | Runs our Flask app in containers |
| **Cloud Build API** | Builds our Docker container in the cloud |
| **Artifact Registry API** | Stores our container images |
| **Secret Manager API** | Safely stores passwords and API keys (for Stripe later) |
| **Cloud SQL Admin API** | Database for user accounts (Phase 2) |

Each one takes a few seconds to enable. You'll see a blue "ENABLE" button, then it'll change to show API details.

---

## Section 4: Install Google Cloud CLI

The CLI (Command Line Interface) lets you deploy the app from your computer.

1. Download the installer: **https://cloud.google.com/sdk/docs/install**
   - Click "Windows" → Download the installer (.exe)
2. Run the installer — accept all defaults
3. At the end, it will open a terminal window
4. It will ask you to log in — a browser window will open, sign in with your Google account
5. It will ask which project to use — select `Themis Court Path`
6. It will ask for a default region — type: `us-west1` (closest to Arizona)

### Verify it worked:
Open a new terminal (Git Bash or Command Prompt) and type:
```bash
gcloud config list
```
You should see something like:
```
[core]
project = themis-court-path
account = your-email@gmail.com
```

---

## Section 5: Create Artifact Registry Repository

This is where Docker container images are stored. Run this command in your terminal:

```bash
gcloud artifacts repositories create themis-app \
  --repository-format=docker \
  --location=us-west1 \
  --description="Themis Court Path container images"
```

**What this does**: Creates a storage space called "themis-app" in the us-west1 region where our app's Docker images will be saved each time we deploy.

---

## Section 6: Install Docker Desktop (Optional)

Docker lets you test the container locally before deploying. It's optional because Cloud Build can build in the cloud, but it's useful for testing.

1. Download: **https://www.docker.com/products/docker-desktop/**
2. Install — accept defaults, restart if prompted
3. Verify: open terminal and type `docker --version`
   - Should show something like: `Docker version 24.x.x`

---

## Section 7: Verify Everything Works

Run these commands to confirm everything is set up:

```bash
# Check your project is set
gcloud config get-value project
# Should output: themis-court-path

# Check APIs are enabled
gcloud services list --enabled --filter="name:run OR name:cloudbuild OR name:artifactregistry"
# Should list Cloud Run, Cloud Build, Artifact Registry

# Check Artifact Registry repository exists
gcloud artifacts repositories list --location=us-west1
# Should show: themis-app
```

If all three commands show the expected output, **you're ready to deploy!**

---

## Section 8: Estimated Costs

| Usage Level | Requests/Month | Monthly Cost |
|-------------|---------------|--------------|
| Testing (just you) | ~100 | **$0** (free tier) |
| Soft launch (100 users) | ~500 | **$0** (free tier) |
| Early growth (1,000 users) | ~5,000 | **$2-5** |
| Phase 1 target (5,000 users) | ~25,000 | **$10-20** |
| Growth (10,000 users) | ~50,000 | **$30-60** |

**Cloud Run free tier** (every month, no expiration):
- 2 million requests
- 360,000 GB-seconds of compute
- 180,000 vCPU-seconds

We will be well within the free tier for all of Phase 1. You likely won't pay anything for months.

---

## Section 9: What Happens Next

After this setup is complete:

1. **Navigate to your app directory**: `cd I:/child_support_app`
2. **Run the deploy script**: `bash deploy.sh`
   - This uploads your code, builds it in the cloud, and deploys it
   - Takes about 3-5 minutes the first time
3. **You'll get a URL** like: `https://themis-app-xxxxx-uw.a.run.app`
4. **Open that URL** in Chrome — you should see the Themis Court Path landing page!
5. **Set up custom domain**: Add a CNAME record in SiteGround DNS for `app.themiscourtpath.com` → `ghs.googlehosted.com`
6. **Map the domain in Cloud Run**:
   ```bash
   gcloud run domain-mappings create \
     --service themis-app \
     --domain app.themiscourtpath.com \
     --region us-west1
   ```
7. SSL certificate is **automatic** — Google handles HTTPS for you

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Permission denied" errors | Run: `gcloud auth login` and sign in again |
| "API not enabled" | Go to APIs & Services → Library and enable the missing API |
| "Billing not enabled" | Go to Billing and link a payment method |
| "Project not found" | Run: `gcloud config set project themis-court-path` |
| Deploy takes too long | First deploy is slowest (downloading base image). Subsequent deploys are faster. |
| App shows error after deploy | Check logs: `gcloud run logs read --service themis-app --region us-west1` |

---

*GCP Setup Guide — Agent B*
*Prepared for Commander Gary Spear*

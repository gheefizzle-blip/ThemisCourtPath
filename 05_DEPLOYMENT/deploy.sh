#!/bin/bash
# ──────────────────────────────────────────────────────────
# Themis Court Path — Deploy to Google Cloud Run
# ──────────────────────────────────────────────────────────
# Usage:  bash deploy.sh
# Prerequisites:
#   1. Google Cloud SDK installed (gcloud command available)
#   2. Authenticated: gcloud auth login
#   3. Project set: gcloud config set project PROJECT_ID
#   4. APIs enabled: Cloud Run, Cloud Build, Artifact Registry
# ──────────────────────────────────────────────────────────

# ── Configuration ────────────────────────────────────────
# Change these to match your Google Cloud project
PROJECT_ID="themis-court-path"      # Your GCP project ID
REGION="us-west1"                    # Closest region to Arizona
SERVICE_NAME="themis-app"            # Cloud Run service name
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=============================================="
echo "  Themis Court Path — Cloud Run Deployment"
echo "=============================================="
echo ""
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Service:  ${SERVICE_NAME}"
echo "Image:    ${IMAGE_NAME}"
echo ""

# ── Step 1: Verify gcloud is configured ──────────────────
echo ">> Step 1: Verifying gcloud configuration..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "   Setting project to ${PROJECT_ID}..."
    gcloud config set project ${PROJECT_ID}
fi
echo "   Project: ${PROJECT_ID} ✓"
echo ""

# ── Step 2: Build the container image ────────────────────
# This uploads your code to Google Cloud Build, which
# builds the Docker image in the cloud (no local Docker needed)
echo ">> Step 2: Building container image..."
echo "   This uploads your code and builds it in the cloud."
echo "   It may take 2-5 minutes on first build."
echo ""
gcloud builds submit --tag ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo ""
    echo "!! BUILD FAILED — Check the errors above."
    echo "   Common fixes:"
    echo "   - Run: gcloud services enable cloudbuild.googleapis.com"
    echo "   - Run: gcloud services enable containerregistry.googleapis.com"
    echo "   - Make sure Dockerfile exists in current directory"
    exit 1
fi
echo "   Build complete ✓"
echo ""

# ── Step 3: Deploy to Cloud Run ──────────────────────────
# This creates (or updates) the Cloud Run service with
# the container image we just built
echo ">> Step 3: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --timeout 300 \
    --concurrency 80 \
    --allow-unauthenticated \
    --set-env-vars "FLASK_ENV=production,SOURCE_PDF=/app/templates_pdf/Petition_to_Establish_Child_Support.pdf"

if [ $? -ne 0 ]; then
    echo ""
    echo "!! DEPLOY FAILED — Check the errors above."
    echo "   Common fixes:"
    echo "   - Run: gcloud services enable run.googleapis.com"
    echo "   - Check billing is enabled on the project"
    exit 1
fi

# ── Step 4: Get the live URL ─────────────────────────────
echo ""
echo "=============================================="
echo "  DEPLOYMENT SUCCESSFUL!"
echo "=============================================="
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region ${REGION} \
    --format "value(status.url)" 2>/dev/null)
echo ""
echo "  Your app is live at:"
echo "  ${SERVICE_URL}"
echo ""
echo "  Next steps:"
echo "  1. Open that URL in Chrome to verify it works"
echo "  2. Add a CNAME record for app.themiscourtpath.com"
echo "     pointing to ghs.googlehosted.com"
echo "  3. Map the custom domain in Cloud Run:"
echo "     gcloud run domain-mappings create \\"
echo "       --service ${SERVICE_NAME} \\"
echo "       --domain app.themiscourtpath.com \\"
echo "       --region ${REGION}"
echo ""
echo "=============================================="

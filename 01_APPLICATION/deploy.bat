@echo off
REM ====================================================
REM  Themis Court Path - Deploy to Google Cloud Run
REM  Windows batch version of deploy.sh
REM ====================================================
REM  Usage:  deploy.bat
REM  Run from the Google Cloud SDK Shell

setlocal

REM ---- Configuration ----
set PROJECT_ID=themis-court-path
set REGION=us-west1
set SERVICE_NAME=themis-app
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo ==============================================
echo   Themis Court Path - Cloud Run Deployment
echo ==============================================
echo.
echo Project:  %PROJECT_ID%
echo Region:   %REGION%
echo Service:  %SERVICE_NAME%
echo Image:    %IMAGE_NAME%
echo.

REM ---- Step 1: Verify project ----
echo ^>^> Step 1: Verifying gcloud configuration...
call gcloud config set project %PROJECT_ID%
echo    Project set to %PROJECT_ID%
echo.

REM ---- Step 2: Build the container image ----
echo ^>^> Step 2: Building container image...
echo    This uploads your code and builds it in the cloud.
echo    It may take 3-5 minutes on first build.
echo.
call gcloud builds submit --tag %IMAGE_NAME% .

if errorlevel 1 (
    echo.
    echo !! BUILD FAILED - Check the errors above.
    echo    Common fixes:
    echo    - Run: gcloud services enable cloudbuild.googleapis.com
    echo    - Run: gcloud services enable containerregistry.googleapis.com
    echo    - Make sure Dockerfile exists in current directory
    exit /b 1
)
echo    Build complete
echo.

REM ---- Step 3: Deploy to Cloud Run ----
echo ^>^> Step 3: Deploying to Cloud Run...
call gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
    --region %REGION% ^
    --platform managed ^
    --memory 512Mi ^
    --cpu 1 ^
    --max-instances 10 ^
    --min-instances 0 ^
    --timeout 300 ^
    --concurrency 80 ^
    --allow-unauthenticated ^
    --set-env-vars "FLASK_ENV=production,SOURCE_PDF=/app/templates_pdf/Petition_to_Establish_Child_Support.pdf"

if errorlevel 1 (
    echo.
    echo !! DEPLOY FAILED - Check the errors above.
    echo    Common fixes:
    echo    - Run: gcloud services enable run.googleapis.com
    echo    - Check billing is enabled on the project
    exit /b 1
)

REM ---- Step 4: Get the live URL ----
echo.
echo ==============================================
echo   DEPLOYMENT SUCCESSFUL!
echo ==============================================
echo.
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i
echo   Your app is live at:
echo   %SERVICE_URL%
echo.
echo   Next steps:
echo   1. Open that URL in Chrome to verify it works
echo   2. Add a CNAME record for app.themiscourtpath.com
echo      pointing to ghs.googlehosted.com
echo   3. Map the custom domain in Cloud Run:
echo      gcloud run domain-mappings create ^
echo        --service %SERVICE_NAME% ^
echo        --domain app.themiscourtpath.com ^
echo        --region %REGION%
echo.
echo ==============================================

endlocal

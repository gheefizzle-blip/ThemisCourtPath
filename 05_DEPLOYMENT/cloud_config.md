# Themis Court Path — Cloud Run Configuration
## DRAFT — REQUIRES COMMANDER REVIEW

### Service Configuration

| Parameter | Value | Why |
|-----------|-------|-----|
| **Region** | `us-west1` (Oregon) | Closest GCP region to Arizona — lowest latency for AZ users |
| **Memory** | `512Mi` | PyMuPDF loads entire 29-page PDF into memory during fill operations. 256Mi risks OOM on large documents |
| **CPU** | `1` | Single vCPU is sufficient — PDF fill is mostly I/O, not compute-heavy |
| **Max Instances** | `10` | Limits scaling to 10 containers. At 80 concurrent requests each = 800 simultaneous users. More than enough for Phase 1 |
| **Min Instances** | `0` | Scale to zero when no traffic — saves money. First request after idle takes ~2-3 seconds (cold start) |
| **Timeout** | `300s` | PDF generation typically takes 1-3 seconds, but allows headroom for large documents or slow I/O |
| **Concurrency** | `80` | Each container handles 80 simultaneous requests. Default is 80, appropriate for a Flask/gunicorn app |
| **Authentication** | `allow-unauthenticated` | Public web app — anyone can access the intake form |
| **Port** | `8080` (via $PORT env var) | Cloud Run injects this automatically — gunicorn binds to it |

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `FLASK_ENV` | `production` | Disables debug mode, enables production error handling |
| `SOURCE_PDF` | `/app/templates_pdf/Petition_to_Establish_Child_Support.pdf` | Path to bundled PDF template inside the Docker image |
| `SECRET_KEY` | (set via Secret Manager) | Flask session signing key — Phase 2 |
| `STRIPE_SECRET_KEY` | (set via Secret Manager) | Stripe payment processing — Phase 2 |

### Estimated Monthly Costs

| Usage Level | Requests/Month | Estimated Cost |
|-------------|---------------|----------------|
| Soft launch (100 users) | ~500 | $0 (free tier) |
| Early growth (1,000 users) | ~5,000 | $2-5 |
| Phase 1 target (5,000 users) | ~25,000 | $10-20 |
| Growth (10,000 users) | ~50,000 | $30-60 |

Cloud Run free tier: 2 million requests/month, 360,000 GB-seconds, 180,000 vCPU-seconds.
We will be well within free tier for all of Phase 1.

### Custom Domain Setup

After deployment, to map `app.themiscourtpath.com`:

1. In SiteGround DNS Zone Editor, add:
   - **Type**: CNAME
   - **Host**: `app`
   - **Value**: `ghs.googlehosted.com`

2. In Google Cloud Console or CLI:
   ```bash
   gcloud run domain-mappings create \
     --service themis-app \
     --domain app.themiscourtpath.com \
     --region us-west1
   ```

3. SSL certificate is provisioned automatically by Google (takes ~15 minutes).

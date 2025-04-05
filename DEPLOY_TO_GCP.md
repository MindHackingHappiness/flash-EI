# Deploying EI-harness-lite to Google Cloud Platform

This guide provides step-by-step instructions for deploying the EI-harness-lite Streamlit app to Google Cloud Platform (GCP) using Cloud Run.

## Prerequisites

1. A Google Cloud Platform account with billing enabled
2. Google Cloud CLI installed on your local machine
3. Docker installed on your local machine (optional, as you can use Cloud Build)
4. API keys for the LLM providers you want to use (OpenAI, Anthropic, Gemini, etc.)

## Step 1: Prepare Your Project

The EI-harness-lite project is already set up with a Dockerfile, so you don't need to create one. However, make sure you have:

- The Streamlit app in `app.py` (already included)
- A complete `requirements.txt` file with all dependencies (already included)
- The Dockerfile (already included)

## Step 2: Set Up Google Cloud CLI

```bash
# Install gcloud CLI if you haven't already
# Then authenticate
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Step 3: Store API Keys Securely

It's important to handle API keys securely. Instead of hardcoding them in your application or including them in your Docker image, use Google Cloud Secret Manager:

```bash
# Create secrets for each API key
gcloud secrets create OPENAI_API_KEY --replication-policy="automatic"
gcloud secrets create ANTHROPIC_API_KEY --replication-policy="automatic"
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"
gcloud secrets create GROQ_API_KEY --replication-policy="automatic"

# Add your API keys to the secrets
echo -n "your-openai-api-key" | gcloud secrets versions add OPENAI_API_KEY --data-file=-
echo -n "your-anthropic-api-key" | gcloud secrets versions add ANTHROPIC_API_KEY --data-file=-
echo -n "your-gemini-api-key" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
echo -n "your-groq-api-key" | gcloud secrets versions add GROQ_API_KEY --data-file=-
```

## Step 4: Build and Deploy Your App

```bash
# Build your container using Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ei-harness-lite

# Deploy to Cloud Run with access to secrets
gcloud run deploy ei-harness-lite \
  --image gcr.io/YOUR_PROJECT_ID/ei-harness-lite \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1 \
  --port 8080 \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,GROQ_API_KEY=GROQ_API_KEY:latest"
```

This command:
- Deploys your container to Cloud Run
- Makes it publicly accessible (`--allow-unauthenticated`)
- Sets up environment variables for your API keys using the secrets you created

## Step 5: Access Your App

After deployment completes, the command will output a URL where your app is available. You can also find this URL in the Google Cloud Console under Cloud Run.

```bash
# Get the URL of your deployed app
gcloud run services describe ei-harness-lite --platform managed --region us-central1 --format="value(status.url)"
```

## Additional Configuration Options

### Setting Memory and CPU Limits

For better performance, especially when handling large language models:

```bash
gcloud run deploy ei-harness-lite \
  --image gcr.io/YOUR_PROJECT_ID/ei-harness-lite \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1 \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,GROQ_API_KEY=GROQ_API_KEY:latest"
```

### Setting Concurrency

To handle multiple users simultaneously:

```bash
gcloud run deploy ei-harness-lite \
  --image gcr.io/YOUR_PROJECT_ID/ei-harness-lite \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1 \
  --port 8080 \
  --concurrency 10 \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,GROQ_API_KEY=GROQ_API_KEY:latest"
```

### Setting a Custom Domain

If you want to use a custom domain instead of the default Cloud Run URL:

1. Verify your domain in Google Cloud Console
2. Map the domain to your Cloud Run service:

```bash
gcloud beta run domain-mappings create \
  --service ei-harness-lite \
  --domain your-domain.com \
  --platform managed \
  --region us-central1
```

## Troubleshooting

### Viewing Logs

To view logs from your deployed application:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ei-harness-lite" --limit 50
```

### Checking Container Status

If your deployment fails, check the container status:

```bash
gcloud run revisions list --service ei-harness-lite --platform managed --region us-central1
```

### Testing Locally Before Deployment

You can test your Docker container locally before deploying:

```bash
# Build the Docker image locally
docker build -t ei-harness-lite .

# Run the container locally
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your-openai-api-key \
  -e ANTHROPIC_API_KEY=your-anthropic-api-key \
  -e GEMINI_API_KEY=your-gemini-api-key \
  -e GROQ_API_KEY=your-groq-api-key \
  ei-harness-lite
```

Then access the app at http://localhost:8080

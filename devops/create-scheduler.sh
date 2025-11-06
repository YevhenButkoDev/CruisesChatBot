#!/bin/bash

# Create Cloud Scheduler job to trigger extractor daily at 2 AM
gcloud scheduler jobs create http extractor-daily \
  --schedule="0 2 * * *" \
  --uri="https://cruise-data-extractor-[hash]-uc.a.run.app" \
  --http-method=POST \
  --location=europe-central2 \
  --time-zone="Europe/Kiev"

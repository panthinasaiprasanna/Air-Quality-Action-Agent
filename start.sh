#!/bin/bash
# Start script for Daily Air Quality Action Agent
export IBM_CLOUD_API_KEY=EMTjVUC0i6zGx9FYZeSqvbUziWZmWxKb36lQ7rFuxnop
export IBM_WATSONX_PROJECT_ID=5c57af7a-46ee-4b47-9eea-fd510a97202c
export IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
export PORT=5000

echo "🚀 Starting Air Quality Action Agent..."
python3 app.py

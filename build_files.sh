#!/bin/bash

# Build script for Vercel deployment
echo "Building Kopi Hayf..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📥 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build completed successfully!"
#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Skip migrations and superuser creation during build
# MongoDB connection will happen at runtime
echo "Build completed successfully. Migrations will run at runtime."

#!/bin/bash
set -e

# Function to wait for MongoDB to be ready
wait_for_mongodb() {
  echo "Waiting for MongoDB to be ready..."
  
  # Try to connect to MongoDB
  for i in {1..30}; do
    if mongo mongodb:27017/test --eval "db.stats()" > /dev/null 2>&1; then
      echo "MongoDB is ready!"
      return 0
    fi
    echo "Waiting for MongoDB... attempt $i/30"
    sleep 2
  done
  
  echo "Error: MongoDB did not become ready in time"
  return 1
}

# Wait for MongoDB
wait_for_mongodb

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Create admin user if it doesn't exist
echo "Creating admin user if it doesn't exist..."
python create_admin.py

# Seed the database if it's empty
echo "Seeding the database if it's empty..."
python run_seed.py

# Start the server
echo "Starting the server..."
exec python manage.py runserver 0.0.0.0:8000
#!/bin/bash
# Stop and remove existing container with the name paper-scraper if it exists to avoid conflicts
docker stop paper-scraper 2>/dev/null || true
docker rm paper-scraper 2>/dev/null || true

# Run the container with the name 'paper-scraper'
echo "Starting Paper Scraper container..."
docker run -p 5001:5000 --env-file .env --name paper-scraper paper-scraper

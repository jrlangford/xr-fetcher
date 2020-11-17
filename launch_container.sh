#!/bin/bash
# Build the image
docker build -t xr_fetcher:latest .
# Run server in background
docker run -d --env-file $1 -p 8000:8000 --name xr_fetcher xr_fetcher:latest
# Apply initial migrations and configuration
docker exec xr_fetcher /bin/sh -c "source .venv/bin/activate && ./manage.py migrate && ./manage.py shell -c \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')\""

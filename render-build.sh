#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies from the backend folder
pip install -r backend/requirements.txt

# Add any other build steps here (like database migrations if you used Alembic)

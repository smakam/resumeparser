#!/bin/bash
# Build script for Render deployment
set -e

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install dependencies preferring binary wheels
pip install --prefer-binary -r requirements.txt

echo "Build completed successfully"


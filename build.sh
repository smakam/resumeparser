#!/bin/bash
# Build script for Render deployment
set -e

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install pydantic-core first with binary wheel (has Rust dependency)
pip install --only-binary pydantic-core pydantic

# Install rest of dependencies preferring binary wheels
pip install --prefer-binary -r requirements.txt

echo "Build completed successfully"


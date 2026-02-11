#!/bin/bash

# Only run in remote (web) environments
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

echo "Setting up cloud environment..."

# Install Python package in editable mode
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  echo "Installing package in editable mode..."
  pip install -q -e .
fi

# Install requirements if present
if [ -f "requirements.txt" ]; then
  echo "Installing requirements.txt..."
  pip install -q -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
  echo "Installing requirements-dev.txt..."
  pip install -q -r requirements-dev.txt
fi

# Set environment variables for Python
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo "PYTHONDONTWRITEBYTECODE=1" >> "$CLAUDE_ENV_FILE"
fi

echo "Cloud environment setup complete!"
exit 0

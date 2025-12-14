#!/bin/bash
# Cleanup script for CFP Guardian project

echo "Cleaning up CFP Guardian project..."

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf goc_guardian.egg-info/
rm -rf build/ dist/ *.egg-info/
rm -rf cfp_reviewer_checker/src.egg-info/

# Remove Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null

# Remove editor files
echo "Removing editor temporary files..."
find . -type f -name "*.swp" -delete
find . -type f -name "*.swo" -delete
find . -type f -name "*~" -delete
find . -type f -name ".DS_Store" -delete

echo "Cleanup complete!"
echo ""
echo "Note: .venv/ and .git/ are preserved (as they should be)"

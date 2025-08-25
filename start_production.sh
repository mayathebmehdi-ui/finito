#!/bin/bash

# Production startup script for E-commerce Policy Analyzer
echo "🚀 Starting E-commerce Policy Analyzer (Production Mode)..."

# Install system dependencies if needed
echo "📦 Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv

# Create virtual environment
echo "🔧 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📋 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
python -m playwright install chromium

# Set production environment variables if not already set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT="production"

# Start the application with Gunicorn
echo "🌐 Starting API server..."
echo "📍 API will be available at: http://0.0.0.0:${PORT:-10000}"

exec gunicorn main:app -c gunicorn.conf.py

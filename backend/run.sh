#!/bin/bash

# SusuSave Backend Run Script

echo "🚀 Starting SusuSave Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from env.example..."
    cp env.example .env
    echo "✏️  Please edit .env with your settings before running in production!"
fi

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head || echo "⚠️  Migrations failed or no database configured"

echo ""
echo "✅ Backend ready!"
echo ""
echo "📊 Starting server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


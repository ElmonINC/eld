#!/bin/bash

# 🎉 eld - Quick Start Script
# This script sets up and starts the entire eld application

echo "🎉 Welcome to eld - Every Little Day!"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please update .env with your API keys for better holiday data"
    echo ""
fi

# Build and start containers
echo "🐳 Building Docker containers..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "📊 Running database migrations..."
docker-compose exec -T web python manage.py migrate

echo ""
echo "🎨 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
echo "🌍 Seeding holiday database (this may take a few minutes)..."
docker-compose exec -T web python manage.py seed_holidays

echo ""
echo "=================================="
echo "✨ eld is ready!"
echo "=================================="
echo ""
echo "🌐 Open your browser and visit:"
echo "   App:    http://localhost:8000"
echo "   Admin:  http://localhost:8000/admin"
echo "   Flower: http://localhost:5555"
echo ""
echo "📝 To create an admin user, run:"
echo "   docker-compose exec web python manage.py createsuperuser"
echo ""
echo "🛑 To stop the app:"
echo "   docker-compose down"
echo ""
echo "📖 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🎉 Happy celebrating!"
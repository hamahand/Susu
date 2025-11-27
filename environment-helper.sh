#!/bin/bash

# Development vs Production URL Helper for SusuSave
# This script helps manage different environments

ENVIRONMENT=${1:-"production"}

if [ "$ENVIRONMENT" = "development" ]; then
    echo "🔧 Development Mode"
    echo "Web App URL: http://localhost:3000"
    echo "API URL: http://127.0.0.1:8000"
    echo "Mobile App: Use localhost in Expo"
elif [ "$ENVIRONMENT" = "production" ]; then
    echo "🚀 Production Mode"
    echo "Web App URL: https://sususave.com"
    echo "API URL: https://api.sususave.com"
    echo "Mobile App: Use production URLs"
else
    echo "Usage: $0 [development|production]"
    echo ""
    echo "Examples:"
    echo "  $0 development  # Set up for local development"
    echo "  $0 production  # Set up for production deployment"
fi

echo ""
echo "📱 Mobile App Commands:"
echo "  Development: EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npx expo start --localhost"
echo "  Production:  EXPO_PUBLIC_API_URL=https://api.sususave.com npx expo start"
echo ""
echo "🌐 Web App Commands:"
echo "  Development: npm run dev"
echo "  Production:  npm run build && npm run preview"

#!/bin/bash

echo "🚀 Spam Sniffer Setup Script"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create .env file if it doesn't exist
if [ ! -f "frontend/.env" ]; then
    echo "📝 Creating frontend/.env file..."
    cat > frontend/.env << EOF
# Google OAuth2 Configuration
# Replace these with your actual Google API credentials
VITE_REACT_APP_CLIENT_ID=your_google_client_id_here
VITE_REACT_APP_API_KEY=your_google_api_key_here
VITE_REACT_APP_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify
EOF
    echo "✅ Created frontend/.env file"
else
    echo "✅ frontend/.env file already exists"
fi

# Check if Google credentials are configured
if grep -q "your_google_client_id_here" frontend/.env; then
    echo ""
    echo "⚠️  IMPORTANT: You need to configure your Google API credentials!"
    echo ""
    echo "📋 Setup Instructions:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a new project or select existing one"
    echo "3. Enable the Gmail API"
    echo "4. Create OAuth2 credentials"
    echo "5. Update the frontend/.env file with your credentials"
    echo ""
    echo "🔗 For detailed instructions, see the README.md file"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

echo ""
echo "🐳 Building and starting containers..."
docker-compose down
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Access your application:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend API: http://localhost:5000"
    echo ""
    echo "📊 Check service status:"
    echo "   docker-compose ps"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
else
    echo "❌ Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

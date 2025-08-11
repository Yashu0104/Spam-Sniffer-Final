@echo off
echo 🚀 Spam Sniffer Setup Script
echo ==============================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available. Please install Docker Compose.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Create .env file if it doesn't exist
if not exist "frontend\.env" (
    echo 📝 Creating frontend\.env file...
    (
        echo # Google OAuth2 Configuration
        echo # Replace these with your actual Google API credentials
        echo VITE_REACT_APP_CLIENT_ID=your_google_client_id_here
        echo VITE_REACT_APP_API_KEY=your_google_api_key_here
        echo VITE_REACT_APP_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify
    ) > frontend\.env
    echo ✅ Created frontend\.env file
) else (
    echo ✅ frontend\.env file already exists
)

REM Check if Google credentials are configured
findstr "your_google_client_id_here" frontend\.env >nul
if %errorlevel% equ 0 (
    echo.
    echo ⚠️  IMPORTANT: You need to configure your Google API credentials!
    echo.
    echo 📋 Setup Instructions:
    echo 1. Go to https://console.cloud.google.com/
    echo 2. Create a new project or select existing one
    echo 3. Enable the Gmail API
    echo 4. Create OAuth2 credentials
    echo 5. Update the frontend\.env file with your credentials
    echo.
    echo 🔗 For detailed instructions, see the README.md file
    echo.
    pause
)

echo.
echo 🐳 Building and starting containers...
docker-compose down
docker-compose up --build -d

echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Services are running!
    echo.
    echo 🌐 Access your application:
    echo    Frontend: http://localhost:5173
    echo    Backend API: http://localhost:5000
    echo.
    echo 📊 Check service status:
    echo    docker-compose ps
    echo.
    echo 📝 View logs:
    echo    docker-compose logs -f
    echo.
    echo 🛑 Stop services:
    echo    docker-compose down
) else (
    echo ❌ Services failed to start. Check logs with: docker-compose logs
    pause
    exit /b 1
)

pause

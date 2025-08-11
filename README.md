# Spam Sniffer - Email Spam Detection System

A full-stack web application that analyzes Gmail emails using machine learning to detect spam and promotional content.

## Features

- 🔐 **Gmail OAuth2 Integration** - Secure login with Google accounts
- 🤖 **ML-Powered Spam Detection** - Uses trained models to classify emails
- 📊 **Real-time Analytics** - Visual charts showing spam vs legitimate email distribution
- 📝 **Email Summarization** - AI-powered email content summarization
- 🎨 **Modern UI** - Beautiful, responsive interface with dark theme
- 🐳 **Docker Support** - Easy deployment with Docker Compose

## Tech Stack

### Backend
- **Flask** - Python web framework
- **MongoDB** - Database for user accounts
- **scikit-learn** - Machine learning models
- **Google Gmail API** - Email access
- **sumy** - Text summarization

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Google API Client** - Gmail integration

## Prerequisites

1. **Google Cloud Console Setup**
   - Create a Google Cloud Project
   - Enable Gmail API
   - Create OAuth2 credentials
   - Download client secret file

2. **Docker & Docker Compose**
   - Install Docker Desktop
   - Ensure Docker Compose is available

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Spam-Sniffer-Final
```

### 2. Configure Google API Credentials

#### Option A: Using Environment Variables
Create a `.env` file in the `frontend` directory:
```env
VITE_REACT_APP_CLIENT_ID=your_google_client_id_here
VITE_REACT_APP_API_KEY=your_google_api_key_here
VITE_REACT_APP_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify
```

#### Option B: Using Docker Compose Environment
Update the `docker-compose.yml` file with your credentials:
```yaml
environment:
  - VITE_REACT_APP_CLIENT_ID=your_actual_client_id
  - VITE_REACT_APP_API_KEY=your_actual_api_key
  - VITE_REACT_APP_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify
```

### 3. Set Up Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized JavaScript origins:
     - `http://localhost:5173`
     - `http://127.0.0.1:5173`
   - Add authorized redirect URIs:
     - `http://localhost:5173`
     - `http://127.0.0.1:5173`
5. Copy the Client ID and API Key to your environment variables

### 4. Run with Docker Compose
```bash
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **MongoDB**: localhost:27017

### 5. Access the Application
1. Open http://localhost:5173 in your browser
2. Click "Login with Gmail"
3. Authorize the application to access your Gmail
4. View and analyze your emails!

## Development Setup

### Backend Development
```bash
cd spam-sniffer-backend
pip install -r requirements.txt
python app.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Backend API (Port 5000)

- `GET /health` - Health check
- `POST /add_account` - Add Gmail account
- `POST /get_emails` - Fetch emails
- `POST /refresh_emails` - Refresh email list
- `POST /remove_account` - Remove Gmail account
- `POST /check_spam` - Analyze email for spam

## Troubleshooting

### Common Issues

#### 1. "Google API credentials not configured"
**Solution**: Set up your Google OAuth2 credentials as described in the setup section.

#### 2. "Failed to initialize Google API client"
**Solution**: 
- Check that your Client ID and API Key are correct
- Ensure the Gmail API is enabled in Google Cloud Console
- Verify authorized origins include `http://localhost:5173`

#### 3. "MongoDB connection failed"
**Solution**: 
- The app will work with mock data if MongoDB is unavailable
- For production, ensure MongoDB is running: `docker-compose up mongo`

#### 4. "ML model files not found"
**Solution**: 
- The app uses mock models if the trained models are missing
- For production, ensure `spam_classifier.pkl` and `tfidf_vectorizer.pkl` are present

#### 5. "Failed to fetch emails"
**Solution**:
- Check that you're logged in with Gmail
- Verify the Gmail API is enabled
- Check browser console for detailed error messages

#### 6. Docker containers not starting
**Solution**:
```bash
# Clean up and restart
docker-compose down
docker system prune -f
docker-compose up --build
```

### Environment Variables Reference

#### Frontend (.env file)
```env
VITE_REACT_APP_CLIENT_ID=your_google_client_id
VITE_REACT_APP_API_KEY=your_google_api_key
VITE_REACT_APP_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify
```

#### Backend (docker-compose.yml)
```yaml
environment:
  - MONGO_URI=mongodb://mongo:27017
  - GOOGLE_CLIENT_SECRET=your_google_client_secret_file
  - FLASK_APP=app.py
  - FLASK_ENV=development
```

## Project Structure

```
Spam-Sniffer-Final/
├── docker-compose.yml          # Main Docker configuration
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx            # Main app component
│   │   ├── GmailClient.jsx    # Gmail integration
│   │   └── ...
│   ├── package.json
│   └── Dockerfile
├── spam-sniffer-backend/       # Flask backend
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── spam_classifier.pkl    # Trained ML model
│   ├── tfidf_vectorizer.pkl   # TF-IDF vectorizer
│   └── Dockerfile
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the browser console for error messages
3. Check Docker logs: `docker-compose logs`
4. Create an issue with detailed error information

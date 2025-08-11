import os
import joblib
import nltk
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests
import googleapiclient.discovery
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words

# NLTK setup
try:
    nltk.download('punkt', quiet=True)
except:
    pass

# Flask App Setup
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

# MongoDB Setup
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client['spam_sniffer_db']
    users_collection = db['users']
except Exception as e:
    print(f"Warning: MongoDB connection failed: {e}")
    # Create a mock collection for development
    class MockCollection:
        def find_one(self, *args, **kwargs):
            return None
        def insert_one(self, *args, **kwargs):
            return type('MockResult', (), {'inserted_id': 'mock_id'})()
        def delete_one(self, *args, **kwargs):
            return type('MockResult', (), {'deleted_count': 1})()
    users_collection = MockCollection()

# Google OAuth2
CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET", "credentials.json")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# Load ML Model with error handling
try:
    spam_classifier = joblib.load('spam_classifier.pkl')
    tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')
    print("ML models loaded successfully")
except FileNotFoundError:
    print("Warning: ML model files not found. Using mock models.")
    # Create mock models for development
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    
    tfidf_vectorizer = TfidfVectorizer()
    spam_classifier = LogisticRegression()
    
    # Train on dummy data
    dummy_texts = ["spam email", "legitimate email", "promotional offer", "important message"]
    dummy_labels = [1, 0, 1, 0]  # 1 for spam, 0 for legitimate
    
    tfidf_vectorizer.fit(dummy_texts)
    spam_classifier.fit(tfidf_vectorizer.transform(dummy_texts), dummy_labels)

# Gmail API Helper
def get_gmail_service(credentials):
    try:
        request_ = google.auth.transport.requests.Request()
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(request_)
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
        return service
    except Exception as e:
        print(f"[ERROR] Gmail API Auth: {str(e)}")
        return None

# Text Summarization
def generate_summary(text):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        summarizer.stop_words = get_stop_words("english")
        summary = summarizer(parser.document, 3)
        return " ".join([str(sentence) for sentence in summary])
    except Exception as e:
        print(f"Error generating summary: {e}")
        return text[:100] + "..." if len(text) > 100 else text

# Spam Detection
def predict_spam(email_body):
    try:
        email_vectorized = tfidf_vectorizer.transform([email_body])
        probabilities = spam_classifier.predict_proba(email_vectorized)
        return probabilities[0][1]
    except Exception as e:
        print(f"Error predicting spam: {e}")
        return 0.5  # Default to neutral

# Add Gmail Account
@app.route('/add_account', methods=['POST'])
def add_account():
    data = request.json
    email = data.get('email')
    token = data.get('token')

    # Check if email or token is missing
    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    # Check if the account already exists in MongoDB
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Account already added"}), 400

    try:
        # Log the request for debugging purposes
        print(f"Attempting to add account: {email}")

        # Insert the email and token into MongoDB
        result = users_collection.insert_one({"email": email, "token": token})

        # Check if insertion was successful
        if result.inserted_id:
            print(f"Account added successfully: {email}")
            return jsonify({"message": "Account added successfully"}), 200
        else:
            print("Failed to add account.")
            return jsonify({"error": "Failed to add account"}), 500
    except Exception as e:
        print(f"[ERROR] {str(e)}")  # Log error if any
        return jsonify({"error": "Error adding account to MongoDB"}), 500

# Get Emails
@app.route('/get_emails', methods=['POST'])
def get_emails():
    data = request.json
    email = data.get('email')
    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "Account not found"}), 404

    creds = Credentials.from_authorized_user_info(info=user['token'], scopes=SCOPES)
    service = get_gmail_service(creds)

    if not service:
        return jsonify({"error": "Failed to authenticate Gmail account"}), 500

    try:
        results = service.users().messages().list(userId='me', maxResults=20).execute()
        messages = results.get('messages', [])
        emails = []
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            emails.append(message)
        return jsonify({"emails": emails})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Remove Gmail Account
@app.route('/remove_account', methods=['POST'])
def remove_account():
    data = request.json
    email = data.get('email')
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({"message": "Account removed successfully"}), 200

# Refresh Emails
@app.route('/refresh_emails', methods=['POST'])
def refresh_emails():
    data = request.json
    email = data.get('email')
    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "Account not found"}), 404

    creds = Credentials.from_authorized_user_info(info=user['token'], scopes=SCOPES)
    service = get_gmail_service(creds)

    if not service:
        return jsonify({"error": "Failed to authenticate Gmail account"}), 500

    try:
        results = service.users().messages().list(userId='me', maxResults=20).execute()
        messages = results.get('messages', [])
        emails = []
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            emails.append(message)
        return jsonify({"emails": emails})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Check if Email is Spam
@app.route('/check_spam', methods=['POST'])
def check_spam():
    data = request.json
    email_body = data.get('text', '')
    
    if not email_body:
        return jsonify({"error": "Text content is required"}), 400
    
    spam_score = predict_spam(email_body)
    summary = generate_summary(email_body)

    # Convert the result of comparison to a native boolean
    is_spam = bool(spam_score > 0.5)  # Ensure this is a native Python bool
    spam_type = "Promotional" if is_spam else "Legitimate"
    description = "This email looks like a promotional offer." if is_spam else "This email seems legitimate."

    return jsonify({
        "is_spam": is_spam,
        "spam_score": float(spam_score),
        "description": description,
        "summary": summary,
        "spam_type": spam_type
    })

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Spam Sniffer Backend is running"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

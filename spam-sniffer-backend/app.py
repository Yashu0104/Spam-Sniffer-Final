import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests
import googleapiclient.discovery
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words
import nltk
from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017")
db = client['your_database_name']
nltk.download('punkt_tab')
# Initialize Flask App
app = Flask(__name__)
# Add this line to enable CORS for all routes
CORS(app, origins=["http://localhost:5173"])

# MongoDB Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client['spam_sniffer_db']
users_collection = db['users']

# Google OAuth2 credentials
CLIENT_SECRET_FILE = 'C:/Users/yashw/OneDrive/Desktop/Spam-Sniffer/credentials.json'  # Path to client secrets
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# Load pre-trained model and TF-IDF vectorizer
spam_classifier = joblib.load('spam_classifier.pkl')  # Load pre-trained model
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')  # Load pre-trained TF-IDF vectorizer

# Helper to get Gmail API service
def get_gmail_service(credentials):
    try:
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
        return service
    except Exception as e:
        return None

# Function to generate summary using TextRank
def generate_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summarizer.stop_words = get_stop_words("english")
    summary = summarizer(parser.document, 3)  # Generate top 3 sentences
    summary_text = " ".join([str(sentence) for sentence in summary])
    return summary_text

# Function to predict spam
def predict_spam(email_body):
    email_vectorized = tfidf_vectorizer.transform([email_body])
    # Get probability for both classes (0 = not spam, 1 = spam)
    probabilities = spam_classifier.predict_proba(email_vectorized)
    return probabilities[0][1]  # The probability of the email being spam

# Add Gmail Account (OAuth flow)
@app.route('/add_account', methods=['POST'])
def add_account():
    data = request.json
    email = data.get('email')
    token = data.get('token')

    # Store token in MongoDB
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Account already added"}), 400
    
    # Save the user data and token to MongoDB
    users_collection.insert_one({"email": email, "token": token})
    
    # Try to get Gmail service
    creds = Credentials.from_authorized_user_info(info=token, scopes=SCOPES)
    service = get_gmail_service(creds)
    
    if not service:
        return jsonify({"error": "Failed to authenticate Gmail account"}), 500
    
    # Fetch inbox data (or any other data you need)
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        return jsonify({"message_count": len(messages)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch Emails for a Specific Gmail Account
@app.route('/get_emails', methods=['POST'])
def get_emails():
    data = request.json
    email = data.get('email')
    
    # Retrieve the user and token from MongoDB
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Account not found"}), 404
    
    creds = Credentials.from_authorized_user_info(info=user['token'], scopes=SCOPES)
    service = get_gmail_service(creds)
    
    if not service:
        return jsonify({"error": "Failed to authenticate Gmail account"}), 500

    # Fetch all emails (not just for one particular day)
    try:
        results = service.users().messages().list(userId='me').execute()  # Fetch all messages
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
    
    # Remove account from MongoDB
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        return jsonify({"error": "Account not found"}), 404
    
    return jsonify({"message": "Account removed successfully"}), 200

# Refresh Gmail Account Emails
@app.route('/refresh_emails', methods=['POST'])
def refresh_emails():
    data = request.json
    email = data.get('email')

    # Retrieve the user and token from MongoDB
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Account not found"}), 404
    
    creds = Credentials.from_authorized_user_info(info=user['token'], scopes=SCOPES)
    service = get_gmail_service(creds)
    
    if not service:
        return jsonify({"error": "Failed to authenticate Gmail account"}), 500

    # Fetch all emails (refreshing all, not just unread)
    try:
        results = service.users().messages().list(userId='me').execute()  # Fetch all messages
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
    email_body = data.get('text')

    # Get spam probability from model
    spam_score = predict_spam(email_body)

    # Generate the summary using TextRank
    summary = generate_summary(email_body)

    # Determine if the email is spam or not
    if spam_score > 0.5:
        is_spam = True
        spam_type = "Promotional"
        spam_description = "This email looks like a promotional offer."
    else:
        is_spam = False
        spam_type = "Legitimate"
        spam_description = "This email seems legitimate."

    return jsonify({
        "is_spam": is_spam,
        "spam_score": spam_score,
        "description": spam_description,
        "summary": summary,
        "spam_type": spam_type
    })

if __name__ == "__main__":
    app.run(debug=True)

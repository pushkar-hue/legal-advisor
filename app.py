from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
from dotenv import load_dotenv
from deep_translator import GoogleTranslator  # Add this import

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the Gemini API
API_KEY = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    raise ValueError("No Gemini API key found. Set GEMINI_API_KEY in your .env file.")

genai.configure(api_key=API_KEY)

# Set the default model name manually
DEFAULT_MODEL_NAME = "gemini-1.5-pro"  # You can change this to "gemini-pro" or "gemini-1.0-pro" if needed.

# Define supported Indian languages
INDIAN_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/languages', methods=['GET'])
def list_languages():
    return jsonify({"languages": INDIAN_LANGUAGES})

@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify({"models": [DEFAULT_MODEL_NAME]})

@app.route('/api/legal-advice', methods=['POST'])
def get_legal_advice():
    try:
        data = request.json
        user_query = data.get('query', '')
        target_language = data.get('language', 'en')  # Default to English
        
        if not user_query:
            return jsonify({"error": "No query provided"}), 400
        
        # Initialize the model
        model = genai.GenerativeModel(DEFAULT_MODEL_NAME)
        
        # Translate user query to English if it's not already in English
        if target_language != 'en':
            try:
                # Translate to English for processing
                translator = GoogleTranslator(source=target_language, target='en')
                english_query = translator.translate(user_query)
            except Exception as e:
                print(f"Translation error (to English): {e}")
                english_query = user_query  # Fallback to original query
        else:
            english_query = user_query
        
        # Enhanced prompt with legal context
        prompt = f"""
        You are a legal advisory assistant. Provide helpful legal information based on the following query.
        Note that you should provide general information only and not specific legal advice.
        Always recommend consulting with a qualified attorney for specific legal situations.
        
        User Query: {english_query}
        """
        
        # Get response from Gemini
        response = model.generate_content([prompt])
        english_response = response.text
        
        # Translate response back to target language if not English
        if target_language != 'en':
            try:
                translator = GoogleTranslator(source='en', target=target_language)
                translated_response = translator.translate(english_response)
                
                # Also translate the disclaimer
                disclaimer = "This information is for general purposes only and does not constitute legal advice. Please consult with a qualified attorney for specific legal advice."
                translated_disclaimer = translator.translate(disclaimer)
            except Exception as e:
                print(f"Translation error (from English): {e}")
                translated_response = english_response
                translated_disclaimer = "This information is for general purposes only and does not constitute legal advice. Please consult with a qualified attorney for specific legal advice."
        else:
            translated_response = english_response
            translated_disclaimer = "This information is for general purposes only and does not constitute legal advice. Please consult with a qualified attorney for specific legal advice."
        
        return jsonify({
            "response": translated_response,
            "disclaimer": translated_disclaimer,
            "original_language": "en",
            "translated_language": target_language
        })
    
    except Exception as e:
        print(f"Error in get_legal_advice: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    return jsonify({
        "available_models": [DEFAULT_MODEL_NAME],
        "api_key_set": bool(API_KEY),
        "available_languages": INDIAN_LANGUAGES
    })

if __name__ == '__main__':
    app.run(debug=True)
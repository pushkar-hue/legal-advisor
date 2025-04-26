from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the Gemini API
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCXCNEwz7GPIbZb3z0SOoyWlQPXui_vNT8")
if not API_KEY:
    raise ValueError("No Gemini API key found. Set GEMINI_API_KEY in your .env file.")

genai.configure(api_key=API_KEY)

# Set the default model name manually
DEFAULT_MODEL_NAME = "gemini-1.5-pro"  # You can change this to "gemini-pro" or "gemini-1.0-pro" if needed.

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify({"models": [DEFAULT_MODEL_NAME]})

@app.route('/api/legal-advice', methods=['POST'])
def get_legal_advice():
    try:
        data = request.json
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "No query provided"}), 400
        
        # Initialize the model
        model = genai.GenerativeModel(DEFAULT_MODEL_NAME)
        
        # Enhanced prompt with legal context
        prompt = f"""
        You are a legal advisory assistant. Provide helpful legal information based on the following query. 
        Note that you should provide general information only and not specific legal advice. 
        Always recommend consulting with a qualified attorney for specific legal situations.
        
        User Query: {user_query}
        """
        
        # Get response from Gemini
        response = model.generate_content([prompt])
        
        return jsonify({
            "response": response.text,
            "disclaimer": "This information is for general purposes only and does not constitute legal advice. Please consult with a qualified attorney for specific legal advice."
        })
    
    except Exception as e:
        print(f"Error in get_legal_advice: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    return jsonify({
        "available_models": [DEFAULT_MODEL_NAME],
        "api_key_set": bool(API_KEY)
    })

if __name__ == '__main__':
    app.run(debug=True)

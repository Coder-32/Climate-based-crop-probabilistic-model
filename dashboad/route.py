import os
from flask import Blueprint, flash, redirect, render_template, request, url_for, session, jsonify
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/dashboard/static'
)

API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or 'AIzaSyCu2IEGul8FywG9E1S9XYtXwJbv4eSNOJ4'

def get_gemini_client():
    key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or API_KEY
    if key and key != 'your-gemini-api-key-here':
        try:
            return genai.Client(api_key=key)
        except Exception:
            return None
    return None

client = get_gemini_client()

@dashboard_bp.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        print("No user in session, redirecting to home.")
        flash("Please log in to access the dashboard.")
        return redirect(url_for('home.login'))
    
    name = user.get('name', 'Farmer')
    location = user.get('location', 'Kolkata')
    user_type = session.get('user_type', 'farmer')
    return render_template('dashboard.html', user=user, location=location, name=name, user_type=user_type)

@dashboard_bp.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'response': 'Please provide a message.'})
    
    active_client = client or get_gemini_client()
    if active_client:
        try:
            prompt = f"You are an agricultural assistant chatbot for farmers. Provide helpful, concise advice on farming, crops, weather, and related topics. User message: {user_message}"
            response = active_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            bot_response = response.text
            return jsonify({'response': bot_response})
        except Exception as e:
            print(f"Chatbot Gemini warning: {e}")
    
    # Fallback helpful response when Gemini is not reachable or API key needs configuration
    return jsonify({
        'response': f"For '{user_message}': Ensure balanced NPK fertilization, maintain recommended soil moisture, and check drainage based on the current weather forecast. (Tip: Set GEMINI_API_KEY in .env for custom live AI responses)."
    })

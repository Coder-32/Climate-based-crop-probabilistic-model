from flask import Blueprint, flash, redirect, render_template, request, url_for, session, jsonify
import google.genai as genai

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/dashboard/static'
)

# API Key for chatbot
API_KEY = 'AIzaSyCu2IEGul8FywG9E1S9XYtXwJbv4eSNOJ4'
client = genai.Client(api_key=API_KEY)

@dashboard_bp.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        print("No user in session, redirecting to home.")
        flash("Please log in to access the dashboard.")
        return redirect(url_for('home.home'))
    
    name = user.get('name', 'Farmer')
    location = user.get('location', 'Kolkata')  # Default to Kolkata if not set
    user_type = session.get('user_type', 'farmer')
    return render_template('dashboard.html', user=user, location=location, name=name, user_type=user_type)

@dashboard_bp.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please provide a message.'})
    
    try:
        prompt = f"You are an agricultural assistant chatbot for farmers. Provide helpful, concise advice on farming, crops, weather, and related topics. User message: {user_message}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        bot_response = response.text
        return jsonify({'response': bot_response})
    except Exception as e:
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.'})

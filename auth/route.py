from flask import Blueprint, request, redirect, url_for, session, flash, jsonify, render_template
from dotenv import load_dotenv
import os
import json
import uuid
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

load_dotenv()

# Compatibility Google blueprint stub so existing app.register_blueprint doesn't fail
google_bp = Blueprint('google', __name__)

@google_bp.route('/')
@google_bp.route('/login')
def google_redirect():
    """Redirect legacy Google login attempts to the password-based login."""
    flash('Please sign in with your email and password.', 'info')
    return redirect(url_for('home.login'))

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

# --- Persistent User Store Configuration ---
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

DEFAULT_USERS = {
    'farmer@example.com': {
        'password': 'Farmer123!',
        'aliases': ['farmer123', 'farmer'],
        'name': 'Farmer User',
        'user_type': 'farmer',
        'location': 'Kolkata, India'
    },
    'scientist@example.com': {
        'password': 'Scientist123!',
        'aliases': ['scientist123', 'scientist'],
        'name': 'Dr. Rajan Sharma',
        'user_type': 'researcher',
        'location': 'IARI Research Center, Delhi'
    },
    'researcher@example.com': {
        'password': 'Researcher123!',
        'aliases': ['researcher123', 'researcher'],
        'name': 'Dr. Rajan Sharma',
        'user_type': 'researcher',
        'location': 'IARI Research Center, Delhi'
    }
}


def load_users():
    """Load users from JSON file, falling back to defaults."""
    users = dict(DEFAULT_USERS)
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                stored = json.load(f)
                users.update(stored)
        except Exception as e:
            print(f"Error reading {USERS_FILE}: {e}")
    else:
        save_users(users)
    return users


def save_users(users_dict):
    """Save users to JSON file."""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_dict, f, indent=2)
    except Exception as e:
        print(f"Error saving {USERS_FILE}: {e}")


def verify_password(user, password):
    """Check if password matches stored password or accepted aliases."""
    if not user or not password:
        return False
    if user.get('password') == password:
        return True
    # Check lowercase match or known convenient aliases
    if user.get('password', '').lower() == password.lower():
        return True
    aliases = user.get('aliases', [])
    if password.lower() in [a.lower() for a in aliases]:
        return True
    return False


reset_tokens = {}


def generate_reset_token(email):
    token = uuid.uuid4().hex
    reset_tokens[token] = {
        'email': email,
        'expires': datetime.utcnow() + timedelta(minutes=30)
    }
    return token


def send_reset_email(email, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = 'Password Reset for AgriLab'
    body = (
        f'Hi,\n\nWe received a request to reset the password for {email}.\n'
        f'Click the link below to choose a new password:\n\n{reset_url}\n\n'
        'This link will expire in 30 minutes. If you did not request this, please ignore this email.\n'
    )

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM', smtp_username or 'no-reply@agrilab.com')

    if not smtp_server or not smtp_username or not smtp_password:
        print('\n--- Password Reset Link (SMTP not configured) ---')
        print(f'To: {email}')
        print(f'Reset URL: {reset_url}\n')
        return

    try:
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = email_from
        message['To'] = email
        message.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(message)
    except Exception as e:
        print(f"Error sending email: {e}")


# --- Status Route ---
@auth_bp.route('/status')
def auth_status():
    """Check session authentication status."""
    return {
        "authenticated": 'user' in session,
        "session_user": session.get('user'),
        "user_type": session.get('user_type')
    }


# --- Sign In Route ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    requested_type = data.get('user_type', 'farmer').strip().lower()
    if requested_type == 'scientist':
        requested_type = 'researcher'

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

    users = load_users()
    user = users.get(email)
    if not user or not verify_password(user, password):
        return jsonify({
            'success': False,
            'error': 'Invalid email or password. Use demo accounts or click Sign Up below!'
        }), 401

    user_type = user.get('user_type', requested_type)
    session['user_type'] = user_type
    session['user'] = {
        'name': user.get('name', 'User'),
        'email': email,
        'location': user.get('location', 'Kolkata, India'),
        'user_type': user_type
    }

    # Redirect farmers directly to dashboard, researchers to researcher portal
    redirect_target = 'home.researcher_home' if user_type == 'researcher' else 'dashboard.dashboard'
    return jsonify({'success': True, 'redirect': url_for(redirect_target)})


# --- Sign Up (Registration) Route ---
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip() or 'User'
    location = data.get('location', '').strip() or 'Kolkata, India'
    user_type = data.get('user_type', 'farmer').strip().lower()
    if user_type == 'scientist':
        user_type = 'researcher'

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

    if len(password) < 4:
        return jsonify({'success': False, 'error': 'Password must be at least 4 characters.'}), 400

    users = load_users()
    if email in users:
        return jsonify({'success': False, 'error': 'An account with this email already exists. Please sign in.'}), 400

    users[email] = {
        'password': password,
        'name': name,
        'user_type': user_type,
        'location': location
    }
    save_users(users)

    session['user_type'] = user_type
    session['user'] = {
        'name': name,
        'email': email,
        'location': location,
        'user_type': user_type
    }

    redirect_target = 'home.researcher_home' if user_type == 'researcher' else 'dashboard.dashboard'
    return jsonify({'success': True, 'redirect': url_for(redirect_target)})


# --- Forgot Password Route ---
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'}), 400

    users = load_users()
    if email in users:
        token = generate_reset_token(email)
        send_reset_email(email, token)
    else:
        print(f'Forgot password requested for unknown email: {email}')

    return jsonify({
        'success': True,
        'message': 'If this email is registered, a password reset link has been processed.'
    })


# --- Reset Password Route ---
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_data = reset_tokens.get(token)
    if not token_data or token_data['expires'] < datetime.utcnow():
        reset_tokens.pop(token, None)
        return render_template('reset_password.html', error='This reset link is invalid or has expired.', success=False)

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not password or not confirm_password:
            return render_template('reset_password.html', error='Both password fields are required.', token=token, success=False)
        if password != confirm_password:
            return render_template('reset_password.html', error='Passwords do not match.', token=token, success=False)

        users = load_users()
        email = token_data['email']
        if email in users:
            users[email]['password'] = password
            save_users(users)
        reset_tokens.pop(token, None)
        return render_template('reset_password.html', success=True)

    return render_template('reset_password.html', token=token, email=token_data['email'], success=False)


# --- Legacy Google Login Route (Redirects to Normal Login) ---
@auth_bp.route('/google')
def google_login():
    return redirect(url_for('home.login'))


# --- Logout Route ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.login'))


# --- Set User Type Route ---
@auth_bp.route('/set-user-type/<user_type>', methods=['GET', 'POST'])
def set_user_type(user_type):
    if user_type == 'scientist':
        user_type = 'researcher'
    if user_type in ['farmer', 'researcher']:
        session['user_type'] = user_type
        if 'user' in session:
            session['user']['user_type'] = user_type
        return jsonify({'success': True, 'user_type': user_type})
    return jsonify({'success': False, 'error': 'Invalid user type'}), 400
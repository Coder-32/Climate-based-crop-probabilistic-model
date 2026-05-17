from flask import Blueprint, request, redirect, url_for, session, flash, jsonify, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from dotenv import load_dotenv
import os
import uuid
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.readonly",
    ],
    offline=True,
    reprompt_consent=False
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

# --- Simple in-memory user store for email/password login and password reset ---
mock_users = {
    'farmer@example.com': {
        'password': 'Farmer123!',
        'name': 'Farmer User',
        'user_type': 'farmer'
    },
    'scientist@example.com': {
        'password': 'Scientist123!',
        'name': 'Scientist User',
        'user_type': 'researcher'
    }
}

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
    subject = 'Password Reset for Your App'
    body = (
        f'Hi,\n\nWe received a request to reset the password for {email}.\n'
        f'Click the link below to choose a new password:\n\n{reset_url}\n\n'
        'This link will expire in 30 minutes. If you did not request this, please ignore this email.\n'
    )

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM', smtp_username or 'no-reply@example.com')

    if not smtp_server or not smtp_username or not smtp_password:
        print('--- Password reset email not sent because SMTP is not configured ---')
        print(f'To: {email}')
        print(f'Subject: {subject}')
        print(body)
        return

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = email_from
    message['To'] = email
    message.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)


@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    # --- LOGGING THE TOKEN ---
    print("\n--- OAUTH SIGNAL TRIGGERED ---")
    if token:
        print(f"Token received! Type: {token.get('token_type')}")
        # Be careful printing the full access_token in production,
        # but for debugging, you can see the first 10 chars:
        print(f"Access Token (First 10 chars): {token.get('access_token')[:10]}...")
    else:
        print("No token received.")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        user_data = {
            'name': user_info.get('name', 'User'),
            'email': user_info.get('email', ''),
            'location': 'Kolkata'
        }
        if 'user_type' in session:
            user_data['user_type'] = session['user_type']
        session['user'] = user_data
        print(f"User identity for {user_info.get('email')} saved to session.")

    print("--- SIGNAL FINISHED (Flask-Dance will now save the token to the session) ---\n")

# --- DEBUG ROUTE TO CHECK STATUS ---
@auth_bp.route('/status')
def auth_status():
    """Visit /auth/status in your browser to see if you are truly authorized."""
    return {
        "google_authorized": google.authorized,
        "session_user": session.get('user'),
        "has_token_in_session": "google_oauth_token" in session,
        "token_snippet": str(session.get('google_oauth_token'))[:50] + "..." if "google_oauth_token" in session else None
    }

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    requested_type = data.get('user_type', 'farmer')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required.'}), 400

    user = mock_users.get(email)
    if not user or user.get('password') != password:
        return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401

    user_type = user.get('user_type', requested_type)
    session['user_type'] = user_type
    session['user'] = {
        'name': user.get('name', 'User'),
        'email': email,
        'location': 'Kolkata',
        'user_type': user_type
    }

    redirect_target = 'home.researcher_home' if user_type == 'researcher' else 'home.farmer_home'
    return jsonify({'success': True, 'redirect': url_for(redirect_target)})


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'}), 400

    if email in mock_users:
        token = generate_reset_token(email)
        send_reset_email(email, token)
    else:
        print(f'Forgot password requested for unknown email: {email}')

    return jsonify({
        'success': True,
        'message': 'If this email is registered, a password reset link has been sent.'
    })


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

        mock_users[token_data['email']]['password'] = password
        reset_tokens.pop(token, None)
        return render_template('reset_password.html', success=True)

    return render_template('reset_password.html', token=token, email=token_data['email'], success=False)


@auth_bp.route('/google')
def google_login():
    next_url = request.args.get('next') or request.referrer
    print(f"Checking auth before redirect: {google.authorized}")
    if google.authorized:
        print("Already authorized with Google.")
        if next_url:
            print(f"Redirecting to next URL: {next_url}")
            return redirect(next_url)
        return redirect(url_for('home.home'))

    if next_url:
        print(f"Passing through next URL: {next_url}")
        return redirect(url_for('google.login', next=next_url))

    return redirect(url_for('google.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    print("Session cleared.")
    return redirect(url_for('home.home'))

@auth_bp.route('/set-user-type/<user_type>', methods=['GET', 'POST'])
def set_user_type(user_type):
    print(f"Setting user type to: {user_type}")
    # Map 'scientist' to 'researcher' for backend consistency
    if user_type == 'scientist':
        user_type = 'researcher'
    
    if user_type in ['farmer', 'researcher']:
        session['user_type'] = user_type
        print(f"Session user_type set to: {session.get('user_type')}")
        return jsonify({'success': True, 'user_type': user_type})
    else:
        print(f"Invalid user type: {user_type}")
        return jsonify({'success': False, 'error': 'Invalid user type'}), 400
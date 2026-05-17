from flask import Blueprint, flash, redirect, render_template, request, url_for, session

home_bp = Blueprint(
    'home',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/home/static'
)

@home_bp.route('/researcher')
def researcher_home():
    print("RESEARCHER HOME ROUTE CALLED")
    user = session.get('user')
    print(f"User in session: {user}")
    if not user:
        print("No user in session, redirecting to home")
        return redirect(url_for('home.home'))
    return render_template('researcher.html', user=user)

@home_bp.route('/farmer')
def farmer_home():
    print("FARMER HOME ROUTE CALLED")
    user = session.get('user')
    print(f"User in session: {user}")
    if not user:
        print("No user in session, redirecting to home")
        return redirect(url_for('home.home'))
    return render_template('index.html', user=user)

@home_bp.route('/')
def home():
    print("MAIN HOME ROUTE CALLED")
    user = session.get('user')
    print(f"User in session: {user}")  # Debug print
    
    # Get user type from session
    user_type = session.get('user_type', None)
    if user:
        user_type = user.get('user_type', 'farmer')
    
    print(f"User type determined: {user_type}")
    if user_type == 'researcher':
        print("Rendering researcher template")
        return render_template('researcher.html', user=user)
    print("Rendering farmer template")
    return render_template('index.html', user=user)

@home_bp.route('/login')
def login():
    return render_template('login.html')

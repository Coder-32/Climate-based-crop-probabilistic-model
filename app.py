from flask import Flask, request, jsonify
from home.route import home_bp  
from auth.route import auth_bp, google_bp
from calender.route import calendar_bp
from dashboad.route import dashboard_bp
from showYield.route import showYield_bp
from navigation.route import navigation_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for Flask-Dance sessions
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(google_bp, url_prefix='/login')
app.register_blueprint(calendar_bp, url_prefix='/calendar')
app.register_blueprint(dashboard_bp)
app.register_blueprint(showYield_bp)
app.register_blueprint(navigation_bp)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename

navigation_bp = Blueprint(
    'navigation',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/navigation/static'
)

@navigation_bp.route('/navigation')
def navigation():
    print("NAVIGATION ROUTE CALLED")
    user = session.get('user')
    user_type = session.get('user_type', 'farmer')
    print(f"User in session: {user}")
    if not user:
        print("No user in session, redirecting to home")
        return redirect(url_for('home.home'))
    
    return render_template('navigation.html', user=user, user_type=user_type)

@navigation_bp.route('/get_weather_data')
def get_weather_data():
    """Fetch weather forecast data for visualization."""
    try:
        location = request.args.get('location', 'kolkata')
        csv_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'weatherpredict', 'predictedData',
            f'{location.lower()}_daily_2026_forecast.csv'
        )
        
        if not os.path.exists(csv_path):
            return jsonify({'error': 'CSV not found'}), 404
        
        df = pd.read_csv(csv_path)
        # Ensure required columns exist
        if 'ds' not in df.columns or 'Temp_Avg' not in df.columns:
            return jsonify({'error': 'Invalid CSV format'}), 400
        
        # Convert to list of dicts for JSON
        data = df[['ds', 'Temp_Avg', 'Humidity_Avg', 'Rainfall']].head(365).to_dict('records')
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/upload_research', methods=['POST'])
def upload_research():
    """Handle research report upload from navigation page."""
    if session.get('user_type') != 'researcher':
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'status': 'error', 'message': 'File must be a CSV'}), 400
    
    try:
        df = pd.read_csv(file)
        required_columns = ['location', 'mineral', 'concentration']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'status': 'error', 'message': 'Invalid CSV columns'}), 400
        
        df['concentration'] = pd.to_numeric(df['concentration'], errors='coerce')
        df = df.dropna(subset=['concentration'])
        df['z_score'] = (df['concentration'] - df['concentration'].mean()) / df['concentration'].std()
        df_valid = df[df['z_score'].abs() <= 3]
        discarded = len(df) - len(df_valid)
        df_valid = df_valid.drop(columns=['z_score'])
        
        filepath = os.path.join('static', 'soil_data_research.csv')
        df_valid.to_csv(filepath, index=False)
        
        return jsonify({
            'status': 'success', 
            'message': f'Upload successful. {discarded} deviated rows discarded.',
            'rows_saved': len(df_valid)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


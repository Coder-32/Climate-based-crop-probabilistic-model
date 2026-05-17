from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from geopy.geocoders import Nominatim
import pandas as pd
import os
from werkzeug.utils import secure_filename

from showYield.service import get_crop_prediction

showYield_bp = Blueprint('showYield', __name__, template_folder='templates')


def geocode_location(location_name: str):
    if not location_name:
        return None
    geolocator = Nominatim(user_agent='farmer_app_showyield')
    location = geolocator.geocode(location_name, exactly_one=True, language='en')
    if not location:
        return None
    return location.latitude, location.longitude


@showYield_bp.route('/showYield')
def show_yield():
    crop = request.args.get('crop', '')
    location = request.args.get('location', '')
    return render_template('showYield.html', crop=crop, location=location)


@showYield_bp.route('/getprediction', methods=['POST'])
def get_prediction():
    crop = request.args.get('crop', '') or request.form.get('crop', '') or 'rice'
    location = request.args.get('location', '') or request.form.get('location', '').strip() or 'Kolkata'
    geocoded = geocode_location(location)

    if not geocoded:
        return jsonify({
            'status': 'error',
            'message': f'Unable to geocode location: {location}. Please enter a valid location.'
        }), 400

    latitude, longitude = geocoded
    prediction = get_crop_prediction(crop, latitude, longitude)
    return jsonify(prediction)


@showYield_bp.route('/upload_soil_data', methods=['GET', 'POST'])
def upload_soil_data():
    if session.get('user_type') != 'researcher':
        flash('Access denied. This page is for researchers only.', 'error')
        return redirect(url_for('home.home'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join('static', 'soil_data.csv')
            try:
                df = pd.read_csv(file)
                # Validate columns
                required_columns = ['location', 'mineral', 'concentration']
                if not all(col in df.columns for col in required_columns):
                    flash('CSV must have columns: location, mineral, concentration', 'error')
                    return redirect(request.url)
                # Check data types
                df['concentration'] = pd.to_numeric(df['concentration'], errors='coerce')
                df = df.dropna(subset=['concentration'])
                # Detect outliers using z-score
                df['z_score'] = (df['concentration'] - df['concentration'].mean()) / df['concentration'].std()
                df_valid = df[df['z_score'].abs() <= 3]  # Keep within 3 std devs
                discarded = len(df) - len(df_valid)
                if discarded > 0:
                    flash(f'Discarded {discarded} deviated rows.', 'warning')
                df_valid = df_valid.drop(columns=['z_score'])
                df_valid.to_csv(filepath, index=False)
                flash('Soil data uploaded successfully.', 'success')
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
        else:
            flash('File must be a CSV.', 'error')
        return redirect(request.url)
    return render_template('upload_soil_data.html')

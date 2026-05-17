import joblib
import pandas as pd
import numpy as np
import google.genai as genai
import json
import os
import matplotlib.pyplot as plt
from scipy.stats import norm
from thefuzz import process 
from geopy.geocoders import Nominatim

# ════════════════════════════════════════════════
# 1. GLOBAL INITIALIZATION
# ════════════════════════════════════════════════
# Replace the placeholder below with your own API key or load it from environment variables.
API_KEY = 'your-api-key-here'
PKL_PATH = os.path.join(os.path.dirname(__file__), 'wheat_integrated_v2.pkl')

# --- FOLDER SETUP ---
# We save to 'static' because web browsers can't access 'templates' directly
STATIC_FOLDER = 'static'
IMAGE_NAME = 'yield_risk_analysis.png'
# This creates the full path: 'static/yield_risk_analysis.png'
IMAGE_PATH = os.path.join(STATIC_FOLDER, IMAGE_NAME)

# Ensure the static folder exists so the code doesn't crash
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

try:
    bundle = joblib.load(PKL_PATH)
    model = bundle['model']
    le_state = bundle['le_state']
    le_dist = bundle['le_dist']
    le_crop = bundle['le_crop']
    le_season = bundle['le_season']
    
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize models: {e}")

# ════════════════════════════════════════════════
# 2. CORE PREDICTION FUNCTION
# ════════════════════════════════════════════════
def get_crop_prediction(crop_name, latitude, longitude):
    try:
        # --- A. Reverse Geocoding ---
        geolocator = Nominatim(user_agent="farmer_app_2026")
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')
        
        if not location:
            return {"status": "error", "message": "Location coordinates could not be resolved."}
        
        address = location.raw.get('address', {})
        raw_state = address.get('state', 'Unknown')
        raw_dist  = address.get('state_district', address.get('county', 'Unknown'))

        # --- B. Fuzzy Matching ---
        m_state = process.extractOne(raw_state, le_state.classes_)[0]
        m_dist  = process.extractOne(raw_dist, le_dist.classes_)[0]
        m_crop  = process.extractOne(crop_name.lower(), le_crop.classes_)[0]

        # --- C. NGBoost Prediction ---
        input_df = pd.DataFrame([{
            'Crop_Year': 2026,
            'State_enc': le_state.transform([m_state])[0],
            'District_enc': le_dist.transform([m_dist])[0],
            'Crop_enc': le_crop.transform([m_crop])[0],
            'Season_enc': le_season.transform(["Kharif"])[0],
            'Area': 1.0, 'Annual_Rainfall': 800, 'Fertilizer': 1e8, 'Pesticide': 2e5
        }])

        y_dist = model.pred_dist(input_df)
        mean_yield = float(y_dist.loc[0])
        std_yield  = float(y_dist.scale[0])

        # --- D. Silent Risk Graph Generation ---
        plt.ioff()
        plt.figure(figsize=(10, 5), facecolor='#f4efe6')
        
        x_axis = np.linspace(mean_yield - 4*std_yield, mean_yield + 4*std_yield, 500)
        y_axis = norm.pdf(x_axis, mean_yield, std_yield)
        
        plt.plot(x_axis, y_axis, color='#2d452b', lw=3)
        plt.fill_between(x_axis, y_axis, color='#4caf50', alpha=0.3)
        plt.axvline(mean_yield, color='red', linestyle='--')
        plt.title(f"Yield Probability: {m_crop.title()} in {m_dist}")
        
        # SAVING TO THE NEW STATIC PATH
        plt.savefig(IMAGE_PATH)
        plt.close()

        # --- E. AI Strategy Generation ---
        prompt = f"""
        Act as an Agronomist. Field in {m_dist}, {m_state}. Crop: {m_crop}. 
        Expected Yield: {mean_yield:.2f} T/Ha. Confidence Gap: {std_yield:.2f}.
        Return ONLY a JSON array: [{{"stage": "...", "text": "...", "cost": "₹...", "risk": 15}}]
        """
        
        ai_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        clean_text = ai_response.text.replace('```json', '').replace('```', '').strip()
        roadmap = json.loads(clean_text)

        # --- F. Construct Result ---
        return {
            "status": "success",
            "location": {
                "address": f"{m_dist}, {m_state}",
                "coords": {"lat": latitude, "lon": longitude}
            },
            "prediction": {
                "expected_yield": round(mean_yield, 2),
                "uncertainty_score": round(std_yield, 2),
                # This path is now relative to the root for the frontend to use
                "graph_path": IMAGE_PATH 
            },
            "roadmap": roadmap
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
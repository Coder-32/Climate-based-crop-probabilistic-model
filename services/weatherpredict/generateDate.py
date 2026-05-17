import pandas as pd
import numpy as np
from pathlib import Path

# --- STATISTICAL UTILITIES ---
def calculate_slope(series, window=7):
    """Calculates rate of change (Trend). Positive = Increasing, Negative = Decreasing."""
    if len(series) < window: return 0
    return np.polyfit(range(len(series)), series, 1)[0]

def get_best_date(weather_df, target_temp, target_humid, trend_type):
    """Finds the date with the lowest 'Environmental Distance' and correct Trend."""
    if weather_df.empty:
        raise ValueError("No weather data available for the target month/stage.")

    # Normalize and calculate distance score
    weather_df = weather_df.copy()
    weather_df['score'] = (
        abs(weather_df['Temp_Avg'] - target_temp) + 
        (abs(weather_df['Humidity'] - target_humid) * 0.5) # Humidity is weighted 0.5
    )
    
    # Filter by trend (e.g., we want increasing rain in June/July)
    if trend_type == 'Positive':
        # Sort by best score and highest positive rain slope
        match = weather_df.sort_values(by=['score', 'rain_slope'], ascending=[True, False]).iloc[0]
    elif trend_type == 'Negative':
        # Sort by best score and steepest negative temp slope (cooling down)
        match = weather_df.sort_values(by=['score', 'temp_slope'], ascending=[True, True]).iloc[0]
    else:
        match = weather_df.sort_values(by='score').iloc[0]
        
    return match['Date']

# --- MAIN ENGINE ---
def generate_2026_crop_calendar(crop_csv, weather_csv):
    # Load Data
    df_crop = pd.read_csv(crop_csv)
    df_weather = pd.read_csv(weather_csv)
    
    # Format Weather Data
    df_weather['Date'] = pd.to_datetime(df_weather['ds'])
    df_weather['Month_Name'] = df_weather['Date'].dt.month_name()
    
    # Pre-calculate Trends (Slopes) for the whole year
    df_weather['temp_slope'] = df_weather['Temp_Avg'].rolling(window=7).apply(calculate_slope)
    df_weather['rain_slope'] = df_weather['Rainfall'].rolling(window=7).apply(calculate_slope)
    
    full_calendar = []

    for _, stage in df_crop.iterrows():
        # 1. Isolate the target month from your 2026 forecast
        month_space = df_weather[df_weather['Month_Name'] == stage['Ideal_Month']]
        
        if month_space.empty:
            full_calendar.append({
                "Date": "N/A",
                "Activity": f"MISSING DATA: {stage['Stage']}",
                "Requirements": "No weather forecast available for this stage month"
            })
            continue

        # 2. Find the Exact Statistically Best Date
        exact_start_date = get_best_date(
            month_space, 
            stage['Temp_Target_C'], 
            stage['Humid_Target_Pct'], 
            stage['Rain_Slope_Trend']
        )
        
        # 3. Add Primary Activity
        full_calendar.append({
            "Date": exact_start_date.strftime('%Y-%m-%d'),
            "Activity": f"CRITICAL: Start {stage['Stage']}",
            "Requirements": f"Minerals: {stage['Urea_kg']}kg Urea | Water: {stage['Water_Depth_cm']}cm"
        })
        
        # 4. DYNAMIC TASK GENERATION (Repetitive Maintenance)
        # We loop through the duration of the stage and add watering/checks
        duration = int(stage['Duration_Days'])
        for day_offset in range(1, duration + 1):
            current_date = exact_start_date + pd.Timedelta(days=day_offset)
            
            # Every 4 days: Add Irrigation task if water is needed
            if day_offset % 4 == 0 and stage['Water_Depth_cm'] > 0:
                full_calendar.append({
                    "Date": current_date.strftime('%Y-%m-%d'),
                    "Activity": "MAINTENANCE: Irrigation Check",
                    "Requirements": f"Maintain {stage['Water_Depth_cm']}cm depth"
                })
            
            # Mid-stage: Add a Fertilizer top-up reminder if Urea is required
            if day_offset == (duration // 2) and stage['Urea_kg'] > 0:
                full_calendar.append({
                    "Date": current_date.strftime('%Y-%m-%d'),
                    "Activity": "FERTILIZER: Second Dose",
                    "Requirements": "Apply remaining Nitrogen/Urea"
                })

    return pd.DataFrame(full_calendar).sort_values('Date')

# --- TEST EXECUTION ---
if __name__ == "__main__":
    base_path = Path(__file__).parent
    crop_csv = base_path.parent.parent / "static" / "rice_full_process.csv"
    weather_csv = base_path / "predictedData" / "kolkata_daily_2026_forecast.csv"

    calendar = generate_2026_crop_calendar(crop_csv, weather_csv)

    print("\n" + "="*50)
    print("      2026 AUTOMATED HARVEST CALENDAR (RICE)")
    print("="*50)
    print(calendar.to_string(index=False))

    output_file = base_path / "final_2026_production_schedule.csv"
    calendar.to_csv(output_file, index=False)
    print(f"\n[SUCCESS] Full year schedule saved to {output_file}")
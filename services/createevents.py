import pandas as pd
from pathlib import Path
from services.weatherpredict.generateDate import calculate_slope, get_best_date

BASE_DIR = Path(__file__).resolve().parent
PREDICTED_FOLDER = BASE_DIR / "weatherpredict" / "predictedData"
DEFAULT_LOCATION_KEY = "kolkata"

LOCATION_ALIASES = {
    "bangalore": ["bangalore", "bengaluru", "bengalore"],
    "delhi": ["delhi", "new delhi"],
    "kolkata": ["kolkata", "calcutta"],
    "mumbai": ["mumbai", "bombay"],
    "pune": ["pune", "poona"]
}

MONTH_NUMBER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

CROP_STAGE_TEMPLATES = {
    "rice": [
        {"Stage": "Land Preparation", "Ideal_Month": "June", "Temp_Target_C": 28, "Humid_Target_Pct": 80, "Rain_Slope_Trend": "Positive", "Urea_kg": 30, "Water_Depth_cm": 5, "Duration_Days": 20},
        {"Stage": "Transplanting", "Ideal_Month": "July", "Temp_Target_C": 29, "Humid_Target_Pct": 85, "Rain_Slope_Trend": "Positive", "Urea_kg": 20, "Water_Depth_cm": 5, "Duration_Days": 25},
        {"Stage": "Tillering", "Ideal_Month": "August", "Temp_Target_C": 27, "Humid_Target_Pct": 86, "Rain_Slope_Trend": "Positive", "Urea_kg": 15, "Water_Depth_cm": 5, "Duration_Days": 20},
        {"Stage": "Harvest", "Ideal_Month": "November", "Temp_Target_C": 24, "Humid_Target_Pct": 60, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 0, "Duration_Days": 10}
    ],
    "wheat": [
        {"Stage": "Sowing", "Ideal_Month": "November", "Temp_Target_C": 18, "Humid_Target_Pct": 60, "Rain_Slope_Trend": "Negative", "Urea_kg": 25, "Water_Depth_cm": 3, "Duration_Days": 14},
        {"Stage": "Tillering", "Ideal_Month": "December", "Temp_Target_C": 16, "Humid_Target_Pct": 55, "Rain_Slope_Trend": "Negative", "Urea_kg": 15, "Water_Depth_cm": 2, "Duration_Days": 18},
        {"Stage": "Booting", "Ideal_Month": "January", "Temp_Target_C": 14, "Humid_Target_Pct": 50, "Rain_Slope_Trend": "Positive", "Urea_kg": 10, "Water_Depth_cm": 2, "Duration_Days": 20},
        {"Stage": "Harvest", "Ideal_Month": "April", "Temp_Target_C": 22, "Humid_Target_Pct": 40, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 0, "Duration_Days": 7}
    ],
    "potato": [
        {"Stage": "Planting", "Ideal_Month": "September", "Temp_Target_C": 20, "Humid_Target_Pct": 70, "Rain_Slope_Trend": "Positive", "Urea_kg": 20, "Water_Depth_cm": 4, "Duration_Days": 15},
        {"Stage": "Earthing Up", "Ideal_Month": "October", "Temp_Target_C": 18, "Humid_Target_Pct": 68, "Rain_Slope_Trend": "Negative", "Urea_kg": 15, "Water_Depth_cm": 3, "Duration_Days": 14},
        {"Stage": "Bulb Formation", "Ideal_Month": "November", "Temp_Target_C": 16, "Humid_Target_Pct": 60, "Rain_Slope_Trend": "Negative", "Urea_kg": 10, "Water_Depth_cm": 3, "Duration_Days": 18},
        {"Stage": "Harvest", "Ideal_Month": "December", "Temp_Target_C": 19, "Humid_Target_Pct": 50, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 0, "Duration_Days": 7}
    ],
    "onion": [
        {"Stage": "Transplanting", "Ideal_Month": "October", "Temp_Target_C": 22, "Humid_Target_Pct": 65, "Rain_Slope_Trend": "Negative", "Urea_kg": 15, "Water_Depth_cm": 3, "Duration_Days": 18},
        {"Stage": "Bulb Development", "Ideal_Month": "November", "Temp_Target_C": 20, "Humid_Target_Pct": 60, "Rain_Slope_Trend": "Negative", "Urea_kg": 10, "Water_Depth_cm": 2, "Duration_Days": 20},
        {"Stage": "Curing Preparation", "Ideal_Month": "December", "Temp_Target_C": 18, "Humid_Target_Pct": 45, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 1, "Duration_Days": 10},
        {"Stage": "Harvest", "Ideal_Month": "January", "Temp_Target_C": 23, "Humid_Target_Pct": 40, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 0, "Duration_Days": 7}
    ],
    "moong": [
        {"Stage": "Sowing", "Ideal_Month": "June", "Temp_Target_C": 29, "Humid_Target_Pct": 80, "Rain_Slope_Trend": "Positive", "Urea_kg": 10, "Water_Depth_cm": 4, "Duration_Days": 10},
        {"Stage": "Flowering", "Ideal_Month": "July", "Temp_Target_C": 28, "Humid_Target_Pct": 75, "Rain_Slope_Trend": "Positive", "Urea_kg": 5, "Water_Depth_cm": 3, "Duration_Days": 12},
        {"Stage": "Pod Filling", "Ideal_Month": "August", "Temp_Target_C": 27, "Humid_Target_Pct": 70, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 2, "Duration_Days": 13},
        {"Stage": "Harvest", "Ideal_Month": "September", "Temp_Target_C": 26, "Humid_Target_Pct": 60, "Rain_Slope_Trend": "Negative", "Urea_kg": 0, "Water_Depth_cm": 0, "Duration_Days": 7}
    ]
}

TIMEZONE = "Asia/Kolkata"


def normalize_location(location: str) -> str:
    if not location:
        return DEFAULT_LOCATION_KEY

    normalized = location.strip().lower()
    for key, aliases in LOCATION_ALIASES.items():
        if key in normalized or any(alias in normalized for alias in aliases):
            return key
    return DEFAULT_LOCATION_KEY


def get_weather_csv_for_location(location: str) -> Path:
    location_key = normalize_location(location)
    candidate = PREDICTED_FOLDER / f"{location_key}_daily_2026_forecast.csv"
    if candidate.exists():
        return candidate
    fallback = PREDICTED_FOLDER / f"{DEFAULT_LOCATION_KEY}_daily_2026_forecast.csv"
    return fallback


def load_weather_data(weather_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(weather_csv)
    df['Date'] = pd.to_datetime(df['ds'])
    df['Month_Name'] = df['Date'].dt.month_name()
    df['temp_slope'] = df['Temp_Avg'].rolling(window=7).apply(calculate_slope, raw=False)
    df['rain_slope'] = df['Rainfall'].rolling(window=7).apply(calculate_slope, raw=False)
    return df


def _month_start_date(month_name: str) -> pd.Timestamp:
    month_number = MONTH_NUMBER.get(month_name, 1)
    return pd.Timestamp(year=2026, month=month_number, day=1)


import pandas as pd

def generate_crop_schedule(crop_name: str, location: str = DEFAULT_LOCATION_KEY) -> pd.DataFrame:
    crop_key = crop_name.strip().lower()
    if crop_key not in CROP_STAGE_TEMPLATES:
        crop_key = 'rice'

    template = CROP_STAGE_TEMPLATES[crop_key]
    weather_csv = get_weather_csv_for_location(location)
    df_weather = load_weather_data(weather_csv)

    events = []
    for stage in template:
        month_space = df_weather[df_weather['Month_Name'] == stage['Ideal_Month']]
        if month_space.empty:
            exact_date = _month_start_date(stage['Ideal_Month'])
        else:
            exact_date = get_best_date(
                month_space,
                stage['Temp_Target_C'],
                stage['Humid_Target_Pct'],
                stage['Rain_Slope_Trend']
            )

        base_date = pd.to_datetime(exact_date)
        event_date = base_date.strftime('%Y-%m-%d')

        # Main Stage Event
        events.append({
            'Date': event_date,
            'Activity': f'CRITICAL: {stage["Stage"]} for {crop_key.title()}',
            'Requirements': f"Target temp {stage['Temp_Target_C']}°C · Humidity {stage['Humid_Target_Pct']}% · Water {stage['Water_Depth_cm']}cm"
        })

        # Maintenance and Fertilizer Logic
        duration = int(stage['Duration_Days'])
        for offset in range(1, duration + 1):
            next_date = (base_date + pd.Timedelta(days=offset)).strftime('%Y-%m-%d')
            
            # Weekly Irrigation Check
            if offset % 7 == 0 and stage['Water_Depth_cm'] > 0:
                events.append({
                    'Date': next_date,
                    'Activity': f'MAINTENANCE: Irrigation check for {crop_key.title()}',
                    'Requirements': f'Check water depth of {stage["Water_Depth_cm"]}cm'
                })
            
            # Mid-point Fertilizer Top-up
            if offset == max(1, duration // 2) and stage['Urea_kg'] > 0:
                events.append({
                    'Date': next_date,
                    'Activity': f'FERTILIZER: Top-up for {crop_key.title()}',
                    'Requirements': f'Apply additional {stage["Urea_kg"]}kg Urea'
                })

    schedule = pd.DataFrame(events).sort_values('Date').reset_index(drop=True)
    return schedule


def schedule_to_google_events(schedule: pd.DataFrame, crop_name: str, location: str) -> list[dict]:
    events = []
    for _, row in schedule.iterrows():
        summary = row['Activity']
        description = f"{row.get('Requirements', '')} | Crop: {crop_name.title()} | Location: {location}"
        
        # --- START/END TIME LOGIC ---
        # We transform the 'Date' (YYYY-MM-DD) into a full ISO timestamp
        # This places the event at 8:00 AM on the grid instead of the all-day header
        start_time = f"{row['Date']}T08:00:00"
        end_time = f"{row['Date']}T09:00:00"

        events.append({
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': TIMEZONE
            },
            'end': {
                'dateTime': end_time,
                'timeZone': TIMEZONE
            },
            'reminders': {
                'useDefault': True
            }
        })
    return events
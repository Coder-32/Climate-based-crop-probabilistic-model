import pandas as pd
import requests
from pathlib import Path
from datetime import datetime


LOCATIONS = {
    "kolkata": {"lat": 22.5726, "lon": 88.3639},
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "delhi": {"lat": 28.6139, "lon": 77.2090},
    "pune": {"lat": 18.5204, "lon": 73.8567},
    "bangalore": {"lat": 12.9716, "lon": 77.5946}
}


def generate_weather_csv(location_name):
    location_name = location_name.lower()

    if location_name not in LOCATIONS:
        raise ValueError(
            f"Location '{location_name}' not found. "
            f"Available: {list(LOCATIONS.keys())}"
        )

    lat = LOCATIONS[location_name]["lat"]
    lon = LOCATIONS[location_name]["lon"]

    end_date = datetime.now().strftime("%Y%m%d")
    start_year = datetime.now().year - 10
    start_date = f"{start_year}0101"

    parameters = [
        "T2M",          # Average temperature
        "T2M_MAX",      # Maximum temperature
        "T2M_MIN",      # Minimum temperature
        "RH2M",         # Humidity
        "PRECTOTCORR",  # Rainfall
        "WS10M"         # Wind speed
    ]

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={','.join(parameters)}"
        "&community=RE"
        f"&latitude={lat}"
        f"&longitude={lon}"
        f"&start={start_date}"
        f"&end={end_date}"
        "&format=JSON"
    )

    print(f"Fetching weather data for {location_name.title()}...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()["properties"]["parameter"]

    rows = []

    for date in data["T2M"].keys():
        rows.append({
            "Date": pd.to_datetime(date, format="%Y%m%d"),
            "Year": int(date[:4]),
            "Month": int(date[4:6]),
            "Day": int(date[6:8]),
            "Temp_Avg": data["T2M"].get(date),
            "Temp_Max": data["T2M_MAX"].get(date),
            "Temp_Min": data["T2M_MIN"].get(date),
            "Humidity": data["RH2M"].get(date),
            "Rainfall": data["PRECTOTCORR"].get(date),
            "Wind_Speed": data["WS10M"].get(date)
        })

    df = pd.DataFrame(rows)

    # NASA uses -999 for missing values
    df.replace(-999, pd.NA, inplace=True)

    # Create data folder if not exists
    data_folder = Path(__file__).parent / "data"
    data_folder.mkdir(exist_ok=True)

    file_path = data_folder / f"{location_name}.csv"

    df.to_csv(file_path, index=False)

    print(f"Saved file: {file_path}")
    return df


if __name__ == "__main__":
    city = "kolkata"
    df = generate_weather_csv(city)
    print(df.head())
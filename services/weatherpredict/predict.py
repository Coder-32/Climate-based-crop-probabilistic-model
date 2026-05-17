import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Load the dataset
df = pd.read_csv(Path(__file__).parent / "rawData" / "kolkata.csv")
df['Date'] = pd.to_datetime(df['Date'])

# List of columns we want to predict
columns_to_predict = ['Temp_Avg', 'Rainfall', 'Humidity', 'Wind_Speed']

# This dictionary will store our monthly results
monthly_2026_forecasts = []

print("Training models and generating forecast for 2026...")

for column in columns_to_predict:
    # 2. Prepare data for Prophet (Prophet requires columns named 'ds' and 'y')
    # We remove rows with missing values for the specific column
    train_df = df[['Date', column]].dropna().rename(columns={'Date': 'ds', column: 'y'})
    
    # 3. Initialize and Train (Fit) the Model
    # We enable yearly seasonality because weather follows annual cycles
    model = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=False)
    model.fit(train_df)
    
    # 4. Create a "Future" dataframe reaching the end of 2026
    # We find how many days are between the last date in data and Dec 31, 2026
    last_date = df['Date'].max()
    future_date = pd.to_datetime('2026-12-31')
    days_to_predict = (future_date - last_date).days
    
    future = model.make_future_dataframe(periods=days_to_predict)
    
    # 5. Predict
    forecast = model.predict(future)
    
    # Filter for only 2026 months that were missing
    prediction_2026 = forecast[forecast['ds'] > last_date][['ds', 'yhat']]
    prediction_2026.rename(columns={'yhat': column}, inplace=True)
    
    monthly_2026_forecasts.append(prediction_2026.set_index('ds'))

# 6. Combine all column predictions into one table
final_forecast = pd.concat(monthly_2026_forecasts, axis=1).reset_index()

# 7. Aggregate to Monthly Status
final_forecast['Month'] = final_forecast['ds'].dt.to_period('M')
monthly_status = final_forecast.groupby('Month').mean(numeric_only=True)

# Display the monthly status for 2026
print("\n--- Predicted Monthly Status for 2026 ---")
print(monthly_status)

# Optional: Save to CSV
predicted_data_folder = Path(__file__).parent / "predictedData"
predicted_data_folder.mkdir(exist_ok=True)
monthly_status.to_csv(predicted_data_folder / 'kolkata_monthly_2026_prediction.csv')
final_forecast.to_csv(predicted_data_folder / 'kolkata_daily_2026_forecast.csv', index=False)
import json
from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from binance.client import Client
import os
import csv
from datetime import datetime
import pandas as pd
import numpy as np
from myApp.utils.indicators import calculate_rsi, calculate_macd


# Create your views here.
def home(request):
    return render(request, "index.html")

# Binance API credentials
API_KEY = "yl0KJSuQR3AqjzGFBGckENjyjOJdQTuP47AuRpQa6WR8Kh9OXYrtOAxJFGR2w0AF"
API_SECRET = "eK9JPShyCEInsCmSxfTpjWw5D0aFaU9ks0iFwRNMvvcaAokXRdTdkcuOsRb8aY4w"

# Directory to store historical data
DATA_DIR = "C:\\Users\\PC.DESKTOP-QK1F62J\\Downloads\\Django_mohamed\\Mohamed_Project\\myApp\\historical_data\\historical_data"


def get_data(request):
    if request.method == 'POST':
        # Extract pair and timeframe from the request (default to BTCUSDT and 1h if not provided)
        pair = request.POST.get('pair', 'BTCUSDT')
        timeframe = request.POST.get('timeframe', Client.KLINE_INTERVAL_1HOUR)

        # Generate the filename based on pair, timeframe, and current month
        current_month = datetime.now().strftime('%Y-%m')
        file_name = f"{pair}_{timeframe}_{current_month}.csv"
        file_path = os.path.join(DATA_DIR, file_name)

        # Ensure the directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Check if file exists
        if os.path.exists(file_path):
            # Serve the existing file for download
            print("the file already exists!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)

        # Fetch data from Binance API if the file doesn't exist
        client = Client(api_key=API_KEY, api_secret=API_SECRET)
        klines = client.get_historical_klines(pair, timeframe, "1 month ago UTC")

        # Save the data to a CSV file
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
            for kline in klines:
                writer.writerow([kline[0], kline[1], kline[2], kline[3], kline[4], kline[5]])
            print("the file fetched !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # Serve the newly created file for download
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)

    return JsonResponse({"success": False, "error": "Invalid request method."})


def backtest_rsi(request):
    if request.method == 'POST':
        pair = request.POST.get('pair', 'BTCUSDT')
        timeframe = request.POST.get('timeframe', Client.KLINE_INTERVAL_1HOUR)
        period = int(request.POST.get('period', 14))  # Default RSI period is 14

        # Load historical data
        file_name = f"{pair}_{timeframe}_{datetime.now().strftime('%Y-%m')}.csv"
        file_path = os.path.join(DATA_DIR, file_name)

        if os.path.exists(file_path):
            # Load data from CSV
            data = pd.read_csv(file_path)
            print("we found the data, we will start backtesting")
        else:
            return JsonResponse({"success": False, "error": "Historical data not found."})

        # Ensure 'close' column exists
        if 'Close' not in data.columns:
            return JsonResponse({"success": False, "error": "'close' column missing in data."})

        # Calculate RSI
        data['RSI'] = calculate_rsi(data, period)

        # Example backtesting logic: Buy when RSI < 30, Sell when RSI > 70
        data['Signal'] = np.where(data['RSI'] < 30, 'Buy', np.where(data['RSI'] > 70, 'Sell', 'Hold'))

        # Send processed data back to the frontend
        return JsonResponse({"success": True, "data": data.to_dict(orient='records')})

    return JsonResponse({"success": False, "error": "Invalid request method."})


# def backtest(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         indicator = data.get('indicator')
#         period = data.get('period', 14)
#         pair = data.get('pair', 'BTCUSDT')
#         timeframe = data.get('timeframe', '1h')

#         file_name = f"{pair}_{timeframe}_{datetime.now().strftime('%Y-%m')}.csv"
#         file_path = os.path.join(DATA_DIR, file_name)

#         if not os.path.exists(file_path):
#             return JsonResponse({"success": False, "error": "Historical data not found."})

#         data = pd.read_csv(file_path)

#         if indicator == 'RSI':
#             data['RSI'] = calculate_rsi(data, period)
#             data['Signal'] = np.where(data['RSI'] < 30, 'Buy', np.where(data['RSI'] > 70, 'Sell', 'Hold'))
#         elif indicator == 'MACD':
#             data['MACD'], data['Signal_Line'] = calculate_macd(data, short_period=12, long_period=26, signal_period=9)
#             data['Signal'] = np.where(data['MACD'] > data['Signal_Line'], 'Buy', 'Sell')

#         return JsonResponse({"success": True, "data": data.to_dict(orient='records')})
#     return JsonResponse({"success": False, "error": "Invalid request method."})

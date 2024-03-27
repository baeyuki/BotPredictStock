import requests
import csv
import numpy as np
from datetime import datetime
from time import sleep

def get_binance_data(symbol, interval, limit):
    url = f"https://api.binance.com/api/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error fetching data from Binance API")
        return None

def parse_data(data):
    candles = []
    closes = [float(item[4]) for item in data]  # Lấy giá đóng cửa của từng cây nến

    # Tính toán RSI
    delta = np.diff(closes)
    gain = delta * (delta > 0)
    loss = -delta * (delta < 0)

    avg_gain = np.mean(gain[:14])  # Trung bình cộng lợi nhuận cho 14 cây nến đầu tiên
    avg_loss = np.mean(loss[:14])  # Trung bình cộng lỗ cho 14 cây nến đầu tiên

    for i in range(14, len(closes)):
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        avg_gain = ((avg_gain * 13) + gain[i - 1]) / 14
        avg_loss = ((avg_loss * 13) + loss[i - 1]) / 14

        candles.append({
            "timestamp": datetime.fromtimestamp(data[i][0] / 1000),
            "open": float(data[i][1]),
            "high": float(data[i][2]),
            "low": float(data[i][3]),
            "close": float(data[i][4]),
            "volume": float(data[i][5]),
            "rsi": rsi
        })




    return candles

def save_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'rsi']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def main():
    symbol = 'BTCUSDT'  # BTC/USDT là biểu tượng giao dịch của Bitcoin trên Binance
    interval = '30m'  # Lấy dữ liệu theo từng 30 phút
    limit = 1000  # Số lượng cây nến cần lấy mỗi lần
    total_data_points = 300 # Tổng số điểm dữ liệu cần thu thập
    data = []
    remaining_data_points = total_data_points

    while remaining_data_points > 0:
        if remaining_data_points < limit:
            limit = remaining_data_points
        new_data = get_binance_data(symbol, interval, limit)
        if new_data:
            parsed_data = parse_data(new_data)
            data.extend(parsed_data)
            remaining_data_points -= limit
            print(f"Collected {len(parsed_data)} data points. Remaining: {remaining_data_points}")
            sleep(1)  # Đợi 1 giây trước khi gửi yêu cầu API tiếp theo
        else:
            print("Failed to collect data from Binance API. Stopping.")
            break

    filename = 'bitcoin_data_test.csv'
    save_to_csv(data, filename)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    main()

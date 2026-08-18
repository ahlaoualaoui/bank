import json
import urllib.request

def get_bitcoin_price():
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data["data"]["amount"]
    except Exception as e:
        print(f"Error: {e}")
        return "Price Offline"

def get_ether_price():
    url = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data["data"]["amount"]
    except Exception as e:
        print(f"Error: {e}")
        return "Price Offline"
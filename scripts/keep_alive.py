import time
import requests
from datetime import datetime

URL = "https://fitforge-main-040f867.kuberns.cloud/livez"
INTERVAL = 300  # 5 minutes in seconds

print(f"Starting server keep-alive ping loop for {URL}...")
print(f"Pinging every {INTERVAL} seconds.")

while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = requests.get(URL, timeout=10)
        print(f"[{now}] Pinged {URL} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[{now}] Ping failed: {e}")
    
    time.sleep(INTERVAL)

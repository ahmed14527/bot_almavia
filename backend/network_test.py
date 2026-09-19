# network_test.py
import requests

try:
    r = requests.get("https://egy.almaviva-visa.it/")
    print("Status code:", r.status_code)
except Exception as e:
    print("Error:", e)

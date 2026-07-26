import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY_OPENWEATHER = os.getenv("API_KEY_OPENWEATHER")

lat, lon = 51.507351, -0.127758 

url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    "lat": lat,
    "lon": lon,
    "appid": API_KEY_OPENWEATHER,
    "units": "metric"
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.json())


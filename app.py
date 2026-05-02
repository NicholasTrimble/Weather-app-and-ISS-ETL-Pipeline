import datetime
from zoneinfo import ZoneInfo
from Main import fetch_iss_position
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from database import add_user, remove_user
from utils.weather_helpers import get_weather_data, calculate_visibility
import os
from dotenv import load_dotenv
import utils.astronomy_api as astronomy_api
import requests
from routes.ui import ui_bp
from routes.api import api_bp




load_dotenv()

NEWS_API_KEY = os.getenv("API_KEY_NEWSAPI")

DB_NAME = "iss_pipeline.db"
app = Flask(__name__)


app.register_blueprint(ui_bp)
app.register_blueprint(api_bp)




def get_iss_position():
    import requests
    from datetime import datetime, timezone

    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        latitude = round(float(data["iss_position"]["latitude"]), 2)
        longitude = round(float(data["iss_position"]["longitude"]), 2)
        central = ZoneInfo("America/Chicago")
        timestamp = datetime.now(tz=central).strftime("%b %d, %Y • %I:%M:%S %p %Z")

    except:
        # fallback
        latitude = 51.5
        longitude = -0.1
        timestamp = datetime.now(timezone.utc).isoformat()

    return latitude, longitude, timestamp
    


if __name__ == "__main__":
    app.run(debug=True)

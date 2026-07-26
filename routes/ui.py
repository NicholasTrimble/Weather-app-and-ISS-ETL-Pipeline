from flask import Blueprint, render_template
import sqlite3
import os

ui_bp = Blueprint("ui", __name__)
DB_NAME = "iss_pipeline.db"

@ui_bp.route("/")
def home():
    return render_template("home.html")

@ui_bp.route("/data")
def data_page():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iss_data ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return render_template("data.html", rows=rows)

@ui_bp.route("/map")
def map_page():
    openweather_key = os.getenv("API_KEY_OPENWEATHER", "")
    return render_template("map.html", weather_key=openweather_key)


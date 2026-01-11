from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from database import add_user, remove_user
from utils.weather_helpers import get_weather_data, calculate_visibility
import os
from dotenv import load_dotenv
import utils.astronomy_api as astronomy_api
import requests



load_dotenv()

NEWS_API_KEY = os.getenv("API_KEY_NEWSAPI")

DB_NAME = "iss_pipeline.db"
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/map")
def show_map():
    return render_template("map.html")

@app.route("/news")
def get_news():
    city = request.args.get("city")
    if not city:
        return jsonify({"headlines": ["No city provided."]})

    news_url = "https://newsapi.org/v2/everything"
    params = {
        "q": city,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(news_url, params=params, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        if data.get("status") != "ok":
            print("NewsAPI error:", data)
            return jsonify({"headlines": ["Error fetching news from NewsAPI."]})

        articles = data.get("articles", [])
        headlines = [article["title"] for article in articles]
        if not headlines:
            headlines = ["No recent news found for this city."]
        return jsonify({"headlines": headlines})

    except Exception as e:
        print("Exception in /news route:", e)
        return jsonify({"headlines": ["Error fetching news."]})

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if email:
        add_user(email)
    return redirect("/")


@app.route("/iss_position")
def iss_position():
    import requests
    from datetime import datetime, timezone

    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        latitude = float((data["iss_position"]["latitude"]),4)
        longitude = float((data["iss_position"]["longitude"]),4)
        timestamp = datetime.now(timezone.utc).isoformat()
    except:
        # fallback
        latitude = 51.5
        longitude = -0.1
        timestamp = datetime.now(timezone.utc).isoformat()

    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp
    })


@app.route("/weather_info")
def weather_info_route():
    # Get latitude and longitude from query parameters
    lat = round(float(request.args.get("lat", 51.507351)), 4)  # default London
    lon = round(float(request.args.get("lon", -0.127758)), 4)

    # Determine if it’s night (optional, default True for now)
    is_night_time = True

    # Call weather helper to get full weather info
    weather_info = get_weather_data(lat, lon, is_night_time)

    # Return JSON for JS to read
    return jsonify(weather_info)


@app.route("/star_chart")
def star_chart():
    from flask import request, jsonify

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"}), 400

    try:
        # note the module prefix
        image_url = astronomy_api.generate_star_chart(float(lat), float(lon))
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        print("Star chart error:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/unsubscribe")
def unsubscribe():
    email = request.args.get("email")
    if email:
        remove_user(email)
        return f"Email {email} has been unsubscribed."
    return "No email provided."



@app.route("/data")
def show_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iss_data ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    # Build a simple readable string
    output = ""
    for row in rows:
        output += f"Timestamp: {row[0]}, Latitude: {row[1]}, Longitude: {row[2]}, Overhead: {row[3]}, Is Night: {row[4]}\n"

    return f"""
    <html>
    <head>
        <title>Latest ISS Data</title>
        <style>
            body {{
                background-color: #000;
                color: #fff;
                font-family: 'Arial', sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}
            h1 {{
                font-size: 2em;
                margin-bottom: 20px;
            }}
            pre {{
                background-color: #111;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 2px 2px 8px #444;
            }}
        </style>
    </head>
    <body>
        <h1>Latest ISS Entries</h1>
        <pre>{output}</pre>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
